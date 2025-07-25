# streamlit_app.py

import streamlit as st
import pandas as pd
from data_handler import load_contacts_from_excel
from email_agent import SmartEmailAgent
from email_tool import send_email_message
from config import SENDER_CREDENTIALS, OPENAI_API_KEY, SENDER_EMAIL, SENDER_PASSWORD, FAILED_EMAILS_LOG_PATH
from translations import LANGUAGES, _t # set_language is removed as language will be managed by session_state
from contextlib import contextmanager
import datetime
import tempfile
import os
import shutil
import re

# --- CSS Styling ---
st.markdown("""
<style>
body {
    background: linear-gradient(135deg, #f0f4fc, #c8d8f8);
}
.card {
    background: white;
    border-radius: 12px;
    padding: 1rem;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    margin-bottom: 1rem;
}
.stButton>button {
    width: 100%;
}
/* Style for the back button to appear on the left */
.stButton.st-emotion-cache-1cpxdwl button { /* Adjust this selector if Streamlit class names change */
    float: left;
}
</style>
""", unsafe_allow_html=True)

# --- Page Config ---
# Page title is now dynamically translated
st.set_page_config(layout="wide", page_title=_t("AI Email Assistant"))

# --- Session State Initialization ---
def init_state():
    if 'initialized' not in st.session_state:
        st.session_state.language = 'fr' # Default language
        st.session_state.page = 'generate'
        st.session_state.contacts = []
        st.session_state.contact_issues = []
        st.session_state.attachments = []
        st.session_state.email_template = {"subject": "", "body": ""}
        st.session_state.email_preview = None
        st.session_state.prompt_text = ""
        st.session_state.personalized_email = True # Default to personalized
        st.session_state.email_sending_status = [] # Log for sending process
        st.session_state.sending_summary = {'total_contacts': 0, 'successful': 0, 'failed': 0}
        st.session_state.initialized = True
    
    # Ensure language is always set correctly from session state on rerun
    # The _t function now directly reads from st.session_state.language
    # so we just need to make sure st.session_state.language is updated
    # via the selectbox in the sidebar.


# --- Helper Functions ---
agent = SmartEmailAgent(openai_api_key=OPENAI_API_KEY)

def render_step_indicator(current_step):
    steps = {
        1: _t("1. Email Generation"),
        2: _t("2. Email Preview & Send"),
        3: _t("3. Results")
    }
    cols = st.columns(3)
    for i, (step_num, step_text) in enumerate(steps.items()):
        with cols[i]:
            if step_num == current_step:
                st.markdown(f"**<big>{step_text}</big>**", unsafe_allow_html=True)
            else:
                st.markdown(f"<big>{step_text}</big>", unsafe_allow_html=True)
    st.markdown("---")


@contextmanager
def st_spinner_text(text):
    """Custom context manager for Streamlit spinner with custom text."""
    with st.spinner(text):
        yield

def upload_contacts_file(uploaded_file):
    if uploaded_file is not None:
        # Create a temporary file to save the uploaded content
        with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            temp_path = tmp_file.name

        st.session_state.contacts, st.session_state.contact_issues = load_contacts_from_excel(temp_path)
        os.unlink(temp_path) # Clean up the temporary file

        if st.session_state.contacts:
            st.success(_t("Successfully loaded {count} valid contacts.", count=len(st.session_state.contacts)))
            st.session_state.uploaded_file_name = uploaded_file.name
        else:
            st.warning(_t("No contacts loaded or file is empty/invalid."))
        
        if st.session_state.contact_issues:
            st.warning(_t("Issue(s) encountered:"))
            for issue in st.session_state.contact_issues:
                st.info(issue) # Use info for issues that aren't critical errors

def generate_email_preview():
    if not st.session_state.email_template['subject'] and not st.session_state.email_template['body']:
        st.warning(_t("No email template generated yet."))
        st.session_state.email_preview = None
        return

    st.session_state.email_preview_generated = False # Reset preview status

    with st_spinner_text(_t("Generating email preview for the first contact. This may take a moment...")):
        if st.session_state.contacts:
            first_contact = st.session_state.contacts[0]
            preview_name = first_contact['name']
            preview_email = first_contact['email']
            
            st.session_state.email_sending_status.append(_t("Using first contact for preview: {name}", name=preview_name))

            if st.session_state.personalized_email:
                # Replace placeholders with actual first contact's data for preview
                preview_subject = st.session_state.email_template['subject'].replace("{{Name}}", preview_name).replace("{{Email}}", preview_email)
                preview_body = st.session_state.email_template['body'].replace("{{Name}}", preview_name).replace("{{Email}}", preview_email)
                st.session_state.email_preview = {"subject": preview_subject, "body": preview_body}
            else:
                # For generic preview, display template with placeholders clearly
                st.session_state.email_preview = {
                    "subject": st.session_state.email_template['subject'],
                    "body": st.session_state.email_template['body']
                }
                st.session_state.email_sending_status.append(_t("Email generated with generic placeholders (e.g., {{Name}}, {{Email}}) as personalization is off."))
            
            st.session_state.email_sending_status.append(_t("Email preview generated successfully."))
            st.session_state.email_preview_generated = True # Set preview status
        else:
            st.warning(_t("No contacts available to generate a preview."))
            st.session_state.email_preview = None

def send_all_emails():
    if not st.session_state.contacts:
        st.error(_t("No contacts available to send emails. Please upload contacts first."))
        return
    if not st.session_state.email_template['subject'] or not st.session_state.email_template['body']:
        st.error(_t("No email content to send. Please generate an email template first."))
        return

    st.session_state.email_sending_status = [] # Clear previous log
    st.session_state.sending_summary = {'total_contacts': len(st.session_state.contacts), 'successful': 0, 'failed': 0}
    st.session_state.email_sending_status.append(_t("Email sending process initiated..."))

    # To show progress during sending
    progress_bar = st.progress(0)
    status_text = st.empty()

    total_contacts = len(st.session_state.contacts)

    for i, contact in enumerate(st.session_state.contacts):
        contact_name = contact.get('name', f"Contact {i+1}")
        contact_email = contact['email']

        st.session_state.email_sending_status.append(f"--- [{i+1}/{total_contacts}] Processing contact: {contact_name} ({contact_email}) ---")
        status_text.text(_t("Sending emails...") + f" ({i+1}/{total_contacts})")
        
        # Determine subject and body based on personalization preference
        current_subject = st.session_state.email_template['subject']
        current_body = st.session_state.email_template['body']

        if st.session_state.personalized_email:
            st.session_state.email_sending_status.append(_t("Generating personalized email for {name}...", name=contact_name))
            current_subject = current_subject.replace("{{Name}}", contact_name).replace("{{Email}}", contact_email)
            current_body = current_body.replace("{{Name}}", contact_name).replace("{{Email}}", contact_email)
        # If not personalized, the template already has placeholders, which will be sent as is.

        st.session_state.email_sending_status.append(_t("Attempting Email for {name}...", name=contact_name))

        # Pass attachments if any are uploaded
        attachments_to_send = []
        if st.session_state.attachments:
            for uploaded_file_obj in st.session_state.attachments:
                # For sending, we need the actual bytes content and filename
                attachments_to_send.append((uploaded_file_obj.getvalue(), uploaded_file_obj.name))


        result = send_email_message(
            sender_email=SENDER_EMAIL,
            sender_password=SENDER_PASSWORD,
            to_email=contact_email,
            subject=current_subject,
            body=current_body, # This will now be HTML thanks to email_tool.py fix
            log_path=FAILED_EMAILS_LOG_PATH,
            attachments=attachments_to_send
        )

        if result['status'] == 'success':
            st.session_state.sending_summary['successful'] += 1
            st.session_state.email_sending_status.append(_t("    - Email: success - Email sent to {email} successfully.", email=contact_email))
        else:
            st.session_state.sending_summary['failed'] += 1
            st.session_state.email_sending_status.append(_t("    - Email: error - Failed to send to {email}. Details: {message}", email=contact_email, message=result['message']))
        
        progress_bar.progress((i + 1) / total_contacts)
        st.session_state.email_sending_status.append("") # Add a blank line for readability

    st.session_state.email_sending_status.append(_t("--- Email sending process complete ---"))
    st.session_state.email_sending_status.append(_t("Summary: {successful} successful, {failed} failed/skipped.",
                                                  successful=st.session_state.sending_summary['successful'],
                                                  failed=st.session_state.sending_summary['failed']))
    
    status_text.empty() # Clear the "Sending emails..." text
    progress_bar.empty() # Clear the progress bar

    st.session_state.page = 'results' # Transition to results page
    st.rerun() # Force a rerun to show results page immediately


# --- Page: Email Generation ---
def page_generate():
    render_step_indicator(1)

    st.subheader(_t("1. Email Generation"))

    # File Uploader
    st.markdown("---")
    st.write(_t("Upload an Excel file with contacts (.xlsx)"))
    uploaded_file = st.file_uploader("", type=["xlsx"])
    if uploaded_file is not None and st.session_state.get('last_uploaded_file_id') != uploaded_file.id:
        st.session_state.last_uploaded_file_id = uploaded_file.id
        upload_contacts_file(uploaded_file)
        st.rerun() # Rerun to process file upload and update UI

    if st.session_state.contacts:
        st.info(_t("Total Contacts Loaded") + f": {len(st.session_state.contacts)}")
        
    st.markdown("---")

    # Email Generation Prompt
    st.subheader(_t("Email Generation Prompt"))
    st.write(_t("Enter your prompt for the AI to generate the email template."))
    
    prompt_col, generate_col = st.columns([4, 1])
    with prompt_col:
        st.session_state.prompt_text = st.text_area(
            _t("Your prompt"), 
            value=st.session_state.prompt_text, 
            height=100, 
            key="email_prompt_text_area",
            help=_t("E.g., 'Craft a welcome email for new subscribers, offering a 10% discount on their first purchase.'")
        )
    
    with generate_col:
        st.markdown("<br>", unsafe_allow_html=True) # Add some vertical space to align button
        if st.button(_t("Generate Email Template"), key="generate_email_button", use_container_width=True):
            if st.session_state.prompt_text:
                with st_spinner_text(_t("Generating email template...")):
                    # Ensure agent uses the current language from session state
                    generated_email = agent.generate_email_template(
                        st.session_state.prompt_text,
                        output_language=st.session_state.language # Pass current language
                    )
                    st.session_state.email_template = generated_email
                    if generated_email and generated_email.get("subject"):
                        st.success(_t("Your email has been generated!"))
                    else:
                        st.error(_t("Error generating email. Please try again."))
                st.rerun() # Force rerun to display generated email template
            else:
                st.warning("Please enter a prompt to generate an email.")

    # Display Generated Email Template
    if st.session_state.email_template and st.session_state.email_template.get("subject"):
        st.markdown("---")
        st.subheader(_t("Email Content Preview"))
        st.text_input(_t("Subject:"), value=st.session_state.email_template['subject'], key="generated_subject", disabled=True)
        st.text_area(_t("Body:"), value=st.session_state.email_template['body'], height=300, key="generated_body", disabled=True)

        st.markdown("---")
        st.checkbox(
            _t("Personalized Emails"),
            value=st.session_state.personalized_email,
            key="personalized_email_checkbox",
            help=_t("If checked, emails will be personalized for each contact (e.g., Hi {Name}). Otherwise, a generic template will be used."),
            on_change=lambda: setattr(st.session_state, 'personalized_email', st.session_state.personalized_email_checkbox) # Update session state immediately
        )

        preview_col, next_col = st.columns(2)
        with preview_col:
            if st.button(_t("Preview Email"), key="preview_button", use_container_width=True):
                generate_email_preview() # This function updates st.session_state.email_preview
                st.session_state.page = 'preview'
                st.rerun() # Force a rerun to show preview page immediately

        with next_col:
            if st.button(_t("Send Emails"), key="send_emails_button_generate_page", use_container_width=True):
                # Before moving to send, ensure preview is generated or confirm directly
                if st.session_state.contacts and st.session_state.email_template.get("subject"):
                    st.session_state.page = 'send'
                    st.rerun()
                else:
                    st.warning(_t("Please upload contacts and generate an email template before sending."))

# --- Page: Email Preview & Send ---
def page_preview():
    render_step_indicator(2)

    st.subheader(_t("Email Content Preview"))

    # Back button to return to generation page
    # Removed st.empty() as it was causing a blank block.
    if st.button(_t("Back to Generate Email"), key="back_to_generate_button"):
        st.session_state.page = 'generate'
        st.rerun()

    st.markdown("---")

    if st.session_state.email_preview_generated and st.session_state.email_preview:
        st.subheader(_t("Template Preview (with placeholders if personalization is off)"))
        st.markdown(f"**{_t('Subject:')}** {st.session_state.email_preview['subject']}")
        
        # Display body with adjustable height
        st.markdown(f"**{_t('Body:')}**")
        st.markdown(st.session_state.email_preview['body'], unsafe_allow_html=True) # Keep as markdown for HTML content

        if not st.session_state.personalized_email:
            st.info(_t("The generated email template includes placeholders. To see the actual personalized content, please ensure 'Personalized Emails' is checked."))
            
        st.markdown("---")

        st.subheader(_t("Confirm Send"))
        st.write(f"{_t('Total Contacts Loaded')}: {len(st.session_state.contacts)}")

        if st.button(_t("Confirm Send"), use_container_width=True, key="confirm_send_button_preview_page"):
            send_all_emails() # This function will set page to 'results' and rerun

    else:
        st.warning(_t("No email preview available. Please generate an email template and preview it first."))
        # Add a button to go back to generate if they landed here by mistake
        if st.button(_t("Go to Email Generation"), key="go_to_generate_from_preview"):
            st.session_state.page = 'generate'
            st.rerun()

# --- Page: Results ---
def page_results():
    render_step_indicator(3)
    st.subheader(_t("3. Results"))
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(_t("Total Contacts"), st.session_state.sending_summary['total_contacts'])
    with col2:
        st.metric(_t("Emails Successfully Sent"), st.session_state.sending_summary['successful'])
    with col3:
        st.metric(_t("Emails Failed to Send"), st.session_state.sending_summary['failed'])

    st.markdown("---")

    if st.session_state.sending_summary['failed'] == 0 and st.session_state.sending_summary['successful'] > 0:
        st.success(_t("All emails sent successfully!"))
        st.write(_t("All {count} emails were sent without any issues.", count=st.session_state.sending_summary['total_contacts']))
    elif st.session_state.sending_summary['failed'] > 0:
        st.warning(_t("Sending complete with errors."))
        st.write(_t("Some emails failed to send. Please check the log below for details."))
    
    st.markdown("---")
    
    if st.session_state.email_sending_status:
        with st.expander(_t("Show Activity Log and Errors")):
            log_container = st.container(height=300)
            for log_entry in st.session_state.email_sending_status:
                if "error" in log_entry.lower() or "failed" in log_entry.lower():
                    log_container.error(log_entry)
                elif "success" in log_entry.lower():
                    log_container.success(log_entry)
                else:
                    log_container.write(log_entry) # Use st.write for general log messages

    st.markdown("---")
    if st.button(_t("Start New Email Session"), use_container_width=True):
        # Clear all session state variables to restart the app
        for k in list(st.session_state.keys()):
            del st.session_state[k]
        init_state() # Re-initialize to default state
        st.rerun() # Force a rerun to show the initial page


# --- Main App Logic ---
init_state()

# Sidebar: Language Selection
with st.sidebar:
    st.header(_t("Settings"))
    st.write(_t("Current Language: {lang}", lang=LANGUAGES[st.session_state.language]))
    selected_lang_code = st.selectbox(
        _t("Select your language"),
        options=list(LANGUAGES.keys()),
        format_func=lambda x: LANGUAGES[x],
        index=list(LANGUAGES.keys()).index(st.session_state.language),
        key="language_selector"
    )
    # Update session state language if changed by user
    if selected_lang_code != st.session_state.language:
        st.session_state.language = selected_lang_code
        st.rerun() # Force rerun to apply new language


# Page Routing
if st.session_state.page == 'generate':
    page_generate()
elif st.session_state.page == 'preview':
    page_preview()
elif st.session_state.page == 'send':
    # This page is a placeholder for initiating the send process and immediately
    # redirecting to results after send_all_emails completes.
    send_all_emails() # This will block and then change the page to results
elif st.session_state.page == 'results':
    page_results()