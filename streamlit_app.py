# streamlit_app.py

import streamlit as st
import pandas as pd
from data_handler import load_contacts_from_excel
from email_agent import SmartEmailAgent
from email_tool import send_email_message
from config import SENDER_CREDENTIALS, OPENAI_API_KEY, SENDER_EMAIL, SENDER_PASSWORD, FAILED_EMAILS_LOG_PATH
import tempfile
import os
import shutil
import datetime
import re

# --- IMPORT LANGUAGE HELPER ---
from translations import LANGUAGES, _t, set_language

# --- CSS Styling (Removed potentially conflicting CSS, keeping it minimal for clarity) ---
st.markdown("""
<style>
/* Basic Streamlit adjustments for better appearance */
.stApp {
    background: #f0f4fc; /* Light background */
}
/* Ensure text input and text area elements have appropriate width */
.stTextInput > div > div > input {
    width: 100%;
}
.stTextArea > div > div > textarea {
    width: 100%;
    min-height: 150px; /* Give more space to body text area */
}
/* Custom styling for the step indicators */
.step-indicator {
    display: flex;
    justify-content: space-around;
    margin-bottom: 20px;
}
.step {
    padding: 10px 15px;
    border-radius: 20px;
    background-color: #e0e0e0;
    color: #555;
    font-weight: bold;
    font-size: 0.9em;
}
.step.active {
    background-color: #4CAF50; /* Green for active step */
    color: white;
}
.step.completed {
    background-color: #2196F3; /* Blue for completed step */
    color: white;
}
.stExpander {
    border-radius: 12px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}
.stExpander details summary {
    font-weight: bold;
    color: #2c3e50;
}

/* Remove the block over object text area - This might be a visual glitch or specific element */
/* Targeting generic block-like elements that might overlay text areas */
/* If a specific class or ID is known for the "block", it should be targeted more precisely */
div[data-testid="stVerticalBlock"] > div:not(:has([data-testid="stTextInput"], [data-testid="stTextArea"])) {
    /* This rule tries to target vertical blocks that do NOT contain text inputs/areas.
       Adjust as needed if the "block" is a specific Streamlit component. */
    z-index: auto !important; /* Ensure no overlay issues */
}

/* Specific fix for text areas to ensure they are always on top */
div[data-testid="stTextArea"] {
    position: relative;
    z-index: 10; /* Ensure text area is above other elements if there's a layering issue */
}


</style>
""", unsafe_allow_html=True)


# --- Page Config ---
st.set_page_config(layout="wide", page_title=_t("AI Email Assistant"))

# --- Session State Initialization ---
def init_state():
    if 'initialized' not in st.session_state:
        st.session_state.language = 'fr' # Default to French
        st.session_state.page = 'generate'
        st.session_state.contacts = []
        st.session_state.contact_issues = []
        st.session_state.uploaded_attachments = [] # Renamed from 'attachments' for clarity
        st.session_state.generated_email = None
        st.session_state.email_generation_error = None
        st.session_state.sending_summary = {'total_contacts': 0, 'successful': 0, 'failed': 0}
        st.session_state.email_sending_status = []
        st.session_state.recipient_name = ""
        st.session_state.subject_prompt = ""
        st.session_state.body_prompt = ""
        st.session_state.user_context = "" # Added to store optional user context for AI
        st.session_state.uploaded_file = None # To hold the uploaded Excel file object
        st.session_state.excel_file_path = None # To hold the path to the saved temp Excel file
        st.session_state.initialized = True # Mark as initialized

# Initialize state on app start
init_state()
set_language(st.session_state.language) # Ensure language is set based on session state

# --- Global Variables / Access from config (defined at top scope) ---
selected_sender_email = SENDER_EMAIL
selected_sender_password = SENDER_PASSWORD
# Initialize SmartEmailAgent
agent = SmartEmailAgent(openai_api_key=OPENAI_API_KEY)


# --- Helper Function for Step Indicator ---
def render_step_indicator(current_step):
    steps = {
        1: _t("1. Email Generation"),
        2: _t("2. Preview & Attachments"),
        3: _t("3. Results")
    }
    
    cols = st.columns(len(steps))
    for i, (step_num, step_text) in enumerate(steps.items()):
        if current_step == step_num:
            status_class = "active"
        elif current_step > step_num:
            status_class = "completed"
        else:
            status_class = ""
        
        with cols[i]:
            st.markdown(f'<div class="step {status_class}">{step_text}</div>', unsafe_allow_html=True)

# --- Functions for Page Navigation ---
def go_to_page(page_name):
    st.session_state.page = page_name
    st.experimental_rerun()

# --- Core Functions ---
@st.spinner(_t("Generating email content..."))
def generate_email_content(subject_prompt, body_prompt, user_context, output_language):
    # Combine subject and body prompts for the AI
    full_prompt = f"Subject: {subject_prompt}\nBody: {body_prompt}"
    
    # Generate email template
    generated_email = agent.generate_email_template(
        prompt=full_prompt,
        user_email_context=user_context,
        output_language=output_language
    )
    return generated_email

@st.spinner(_t("Sending emails..."))
def send_all_emails():
    st.session_state.email_sending_status = [] # Clear previous status
    successful_sends = 0
    failed_sends = 0
    total_contacts = len(st.session_state.contacts)

    st.session_state.email_sending_status.append(_t(f"Initiating email send for {total_contacts} contacts..."))
    
    for i, contact in enumerate(st.session_state.contacts):
        contact_name = contact.get('name', contact['email'])
        st.session_state.email_sending_status.append(_t(f"--- [{i+1}/{total_contacts}] Processing contact: {contact_name} ({contact['email']}) ---"))
        
        # Replace placeholders in the generated subject and body
        personalized_subject = st.session_state.generated_email['subject'].replace("{{Name}}", contact.get('name', ''))
        personalized_body = st.session_state.generated_email['body'].replace("{{Name}}", contact.get('name', ''))
        
        # Add other potential placeholders here if your AI generates them
        personalized_subject = personalized_subject.replace("{{Email}}", contact.get('email', ''))
        personalized_body = personalized_body.replace("{{Email}}", contact.get('email', ''))
        
        # Example for Custom_Field - adapt based on your excel columns
        # if 'Custom_Field' in contact:
        #     personalized_subject = personalized_subject.replace("{{Custom_Field}}", contact['Custom_Field'])
        #     personalized_body = personalized_body.replace("{{Custom_Field}}", contact['Custom_Field'])

        st.session_state.email_sending_status.append(_t(f"Attempting to send email to {contact['email']}..."))
        send_result = send_email_message(
            sender_email=selected_sender_email,
            sender_password=selected_sender_password,
            to_email=contact['email'],
            subject=personalized_subject,
            body=personalized_body,
            attachments=st.session_state.uploaded_attachments,
            log_path=FAILED_EMAILS_LOG_PATH
        )

        if send_result['status'] == 'success':
            successful_sends += 1
            st.session_state.email_sending_status.append(_t(f"    - Email: success - Sent to {contact['email']}."))
        else:
            failed_sends += 1
            st.session_state.email_sending_status.append(_t(f"    - Email: error - Failed to send to {contact['email']}. Reason: {send_result['message']}"))
            
    st.session_state.sending_summary = {
        'total_contacts': total_contacts,
        'successful': successful_sends,
        'failed': failed_sends
    }
    st.session_state.email_sending_status.append(_t("--- Email sending process complete ---"))
    st.session_state.email_sending_status.append(_t(f"Summary: {successful_sends} successful, {failed_sends} failed/skipped."))
    
    # Transition to results page after sending
    go_to_page('results')


# --- Page Functions ---

# --- Page: Generate Email ---
def page_generate():
    st.subheader(_t("1. Email Generation"))
    render_step_indicator(1)

    st.write(_t("Compose your email details below."))

    # Sender Email (Read-only as it's from config)
    st.info(_t("Sender Email: {email} (Configured in secrets)").format(email=selected_sender_email))
    
    # Upload Excel for Contacts
    uploaded_file = st.file_uploader(
        _t("Upload an Excel file with contacts (.xlsx)"),
        type=["xlsx"],
        key="excel_uploader"
    )

    if uploaded_file and uploaded_file != st.session_state.uploaded_file:
        st.session_state.uploaded_file = uploaded_file
        # Save the uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            st.session_state.excel_file_path = tmp_file.name
        
        contacts, issues = load_contacts_from_excel(st.session_state.excel_file_path)
        st.session_state.contacts = contacts
        st.session_state.contact_issues = issues
        
        if contacts:
            st.success(_t("Successfully loaded {count} valid contacts.").format(count=len(contacts)))
            if issues:
                st.warning(_t("Some contacts had issues (e.g., missing/invalid emails). They will be skipped."))
                for issue in issues:
                    st.error(issue)
        else:
            st.error(_t("No valid contacts found in the Excel file or an error occurred during loading."))
            if issues:
                for issue in issues:
                    st.error(issue)
        
        st.experimental_rerun() # Rerun to update UI with contact info


    if st.session_state.contacts:
        st.write(_t(f"Currently loaded {len(st.session_state.contacts)} valid contacts."))
        with st.expander(_t("View Loaded Contacts")):
            st.dataframe(pd.DataFrame(st.session_state.contacts))
    elif st.session_state.excel_file_path: # File was uploaded but no valid contacts
         st.error(_t("No valid contacts were loaded from the file. Please check your Excel format."))


    # Email Prompts
    st.markdown("---")
    st.subheader(_t("Email Content Generation"))
    st.text_input(_t("Subject Prompt (e.g., 'A welcome email')"), 
                  value=st.session_state.subject_prompt, 
                  key="subject_prompt_input",
                  placeholder=_t("Enter a subject prompt"))
    
    st.text_area(_t("Body Prompt (e.g., 'Thank them for signing up and offer a link to our tutorial.')"), 
                 value=st.session_state.body_prompt, 
                 key="body_prompt_input",
                 height=150,
                 placeholder=_t("Enter the body prompt"))

    st.text_area(_t("Optional: Additional context/style for AI (e.g., 'Make it formal and concise.')"), 
                 value=st.session_state.user_context, 
                 key="user_context_input",
                 height=100,
                 placeholder=_t("Optional context for AI generation"))

    st.markdown("---")
    
    # Generate Button
    # The first button on the first page is 'Upload an Excel file'.
    # The 'Generate Email' button's behavior: it should trigger AI generation and then move to the next page.
    if st.button(_t("Generate Email"), use_container_width=True, key="generate_email_btn", 
                 disabled=not (st.session_state.subject_prompt_input and st.session_state.body_prompt_input)):
        
        if st.session_state.subject_prompt_input and st.session_state.body_prompt_input:
            with st.spinner(_t("Generating email... This may take a moment.")):
                generated_email = generate_email_content(
                    st.session_state.subject_prompt_input,
                    st.session_state.body_prompt_input,
                    st.session_state.user_context_input,
                    st.session_state.language
                )
            
            if generated_email and not generated_email.get('subject') == 'Error':
                st.session_state.generated_email = generated_email
                st.session_state.email_generation_error = None
                go_to_page('preview') # Change page after successful generation
            else:
                st.error(_t("Error generating email. Please try again. Details: {error_details}").format(error_details=generated_email.get('body', 'Unknown Error')))
                st.session_state.email_generation_error = _t("Error generating email.")
        else:
            st.error(_t("Subject and Body prompts cannot be empty."))
            st.session_state.email_generation_error = _t("Subject and Body prompts cannot be empty.")


# --- Page: Preview & Attachments ---
def page_preview():
    st.subheader(_t("2. Preview & Attachments")) # TRANSLATED
    render_step_indicator(2)

    if st.button(_t("Back to Generation"), use_container_width=True): # TRANSLATED
        go_to_page('generate')

    st.markdown("---")

    if st.session_state.generated_email:
        st.subheader(_t("Generated Email Preview")) # TRANSLATED
        
        # Display email to the first contact for preview purposes
        if st.session_state.contacts:
            first_contact = st.session_state.contacts[0]
            preview_name = first_contact.get('name', _t("Recipient"))
            preview_email = first_contact.get('email', 'N/A')

            st.write(f"**{_t('Email will be sent to')}:** {preview_name} <{preview_email}>") # TRANSLATED

            personalized_subject = st.session_state.generated_email['subject'].replace("{{Name}}", preview_name)
            personalized_body = st.session_state.generated_email['body'].replace("{{Name}}", preview_name)
            
            # Add other potential placeholders here if your AI generates them
            personalized_subject = personalized_subject.replace("{{Email}}", preview_email)
            personalized_body = personalized_body.replace("{{Email}}", preview_email)

            st.write(f"**{_t('Subject')}:** {personalized_subject}") # TRANSLATED
            st.markdown(f"**{_t('Body')}:**") # TRANSLATED
            st.markdown(personalized_body, unsafe_allow_html=True) # Render as HTML
        else:
            st.warning(_t("No contacts loaded to show a personalized preview. Showing generic template."))
            st.write(f"**{_t('Subject')}:** {st.session_state.generated_email['subject']}") # TRANSLATED
            st.markdown(f"**{_t('Body')}:**") # TRANSLATED
            st.markdown(st.session_state.generated_email['body'], unsafe_allow_html=True) # Render as HTML

    else:
        st.warning(_t("No email content has been generated yet. Please go back to the 'Email Generation' page."))
        if st.button(_t("Go to Email Generation")): # TRANSLATED
            go_to_page('generate')
        return

    st.markdown("---")
    st.subheader(_t("Add Attachments (Optional)")) # TRANSLATED
    
    uploaded_files = st.file_uploader(
        _t("Select one or more files"), # TRANSLATED
        type=None, # Allow all file types
        accept_multiple_files=True,
        key="attachment_uploader"
    )

    # Handle attachments
    current_attachments = st.session_state.uploaded_attachments # Use the session state variable
    
    if uploaded_files:
        # Clear previous attachments if new files are uploaded
        if any(f.name not in [prev_f.name for prev_f in current_attachments] for f in uploaded_files):
             # If new files are different, assume user wants to replace
            st.session_state.uploaded_attachments = [] 
            
            for uploaded_file in uploaded_files:
                # Create a temporary file to store the attachment
                with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as tmp_file:
                    tmp_file.write(uploaded_file.getvalue())
                    st.session_state.uploaded_attachments.append(tmp_file.name)
            st.success(_t(f"Successfully added {len(st.session_state.uploaded_attachments)} attachment(s)."))
            st.experimental_rerun() # Rerun to update the list of attachments displayed

    if st.session_state.uploaded_attachments:
        st.write(f"**{_t('Attachments')}:**") # TRANSLATED
        for f_path in st.session_state.uploaded_attachments:
            st.write(f"- {os.path.basename(f_path)}")
        if st.button(_t("Clear Attachments")): # TRANSLATED
            for f_path in st.session_state.uploaded_attachments:
                try:
                    os.remove(f_path) # Clean up temp files
                except OSError:
                    pass
            st.session_state.uploaded_attachments = []
            st.experimental_rerun()
    else:
        st.info(_t("No attachments selected.")) # TRANSLATED


    st.markdown("---")
    if st.button(_t("Confirm Send"), use_container_width=True, 
                 disabled=not (st.session_state.contacts and st.session_state.generated_email)): # TRANSLATED
        send_all_emails() # This function already transitions to results page


# --- Page: Results ---
def page_results():
    st.subheader(_t("3. Results")) # TRANSLATED
    render_step_indicator(3)

    if st.button(_t("Start New Email Session"), use_container_width=True): # TRANSLATED
        # Clear all relevant session state variables
        st.session_state.clear()
        init_state() # Re-initialize to default clean state
        go_to_page('generate') # Go back to the first page immediately
        

    total = st.session_state.sending_summary['total_contacts']
    suc = st.session_state.sending_summary['successful']
    fail = st.session_state.sending_summary['failed']
    
    st.markdown("---")
    if fail == 0 and suc > 0:
        st.success(_t("All emails sent successfully!")) # TRANSLATED
        st.write(_t("All {count} emails were sent without any issues.").format(count=total)) # TRANSLATED
    else:
        st.warning(_t("Sending complete with errors.")) # TRANSLATED
        st.write(_t("Some emails failed to send. Please check the log below for details.")) # TRANSLATED
    
    st.markdown("---")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(_t("Total Contacts"), total) # TRANSLATED
    with col2:
        st.metric(_t("Emails Successfully Sent"), suc) # TRANSLATED
    with col3:
        st.metric(_t("Emails Failed to Send"), fail) # TRANSLATED

    if st.session_state.email_sending_status:
        st.markdown("---")
        with st.expander(_t("Show Activity Log and Errors"), expanded=False): # TRANSLATED
            log_container = st.container(height=300)
            for log_entry in st.session_state.email_sending_status:
                if "error" in log_entry.lower() or "failed" in log_entry.lower():
                    log_container.error(log_entry)
                elif "success" in log_entry.lower():
                    log_container.success(log_entry)
                else:
                    log_container.info(log_entry)


# --- Sidebar: Language Selection ---
with st.sidebar:
    st.image("https://images.unsplash.com/photo-1596551329241-e9702675d045?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w1MDcxMzJ8MHwxfHNlYXJjaHw3MHx8YWklMjBlbWFpbCUyMGFzc2lzdGFudHxlbnwwfHx8fDE3MjE4MzI2NzJ8MA&ixlib=rb-4.0.3&q=80&w=1080", width=100)
    st.title(_t("AI Email Assistant")) # TRANSLATED
    st.markdown("---")
    
    # Language selection
    chosen_language_code = st.selectbox(
        _t("Select your language"), # TRANSLATED
        options=list(LANGUAGES.keys()),
        format_func=lambda x: LANGUAGES[x],
        index=list(LANGUAGES.keys()).index(st.session_state.language),
        key="language_selector"
    )

    if chosen_language_code != st.session_state.language:
        st.session_state.language = chosen_language_code
        set_language(chosen_language_code)
        st.experimental_rerun() # Rerun app to apply new language immediately


# --- Main App Logic (Page Routing) ---
if st.session_state.page == 'generate':
    page_generate()
elif st.session_state.page == 'preview':
    page_preview()
elif st.session_state.page == 'results':
    page_results()

# Cleanup temporary excel file if it exists and is not needed anymore
# This needs to be carefully handled to avoid issues if files are still in use
if st.session_state.get('excel_file_path') and st.session_state.page != 'generate':
    try:
        if os.path.exists(st.session_state.excel_file_path):
            os.remove(st.session_state.excel_file_path)
            st.session_state.excel_file_path = None # Clear the path
    except OSError as e:
        # File might still be in use by pandas or another process
        # print(f"Could not remove temporary Excel file: {e}")
        pass # Suppress error if file is in use. It will be cleaned up eventually.

# Cleanup temporary attachment files (when session ends or app restarts)
# This is tricky in Streamlit as sessions persist, but files should be removed eventually.
# A more robust solution for temp files is often to use a directory that's cleared on app restart.
# For now, let's keep the existing logic and rely on the OS to clean up /tmp.