# streamlit_app.py

import streamlit as st
import pandas as pd
from data_handler import load_contacts_from_excel
from email_agent import SmartEmailAgent
from email_tool import send_email_message
from config import SENDER_EMAIL, SENDER_PASSWORD, OPENAI_API_KEY, FAILED_EMAILS_LOG_PATH
from translations import LANGUAGES, _t, set_language
from contextlib import contextmanager
import datetime
import os
import shutil
import tempfile
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
/* Ensure Streamlit elements don't create extra unwanted space */
div.stActionButton, div.stDownloadButton, div.stFileUploadDropzone {
    margin-bottom: 0.5rem; /* Adjust as needed */
}
</style>
""", unsafe_allow_html=True)

# --- Page Config ---
st.set_page_config(layout="wide", page_title=_t("AI Email Assistant"))

# --- Session State Initialization ---
def init_state():
    if 'initialized' not in st.session_state:
        st.session_state.language = 'fr'
        st.session_state.page = 'generate'
        st.session_state.contacts = []
        st.session_state.contact_issues = []
        st.session_state.attachments = []
        st.session_state.email_sending_status = []
        st.session_state.sending_summary = {'total_contacts':0, 'successful':0, 'failed':0}
        st.session_state.generation_in_progress = False
        st.session_state.sending_in_progress = False
        st.session_state.user_prompt = ''
        st.session_state.user_email_context = ''
        st.session_state.personalize_emails = False
        st.session_state.generic_greeting = ''
        st.session_state.template_subject = ''
        st.session_state.template_body = ''
        st.session_state.editable_subject = ''
        st.session_state.editable_body = ''
        st.session_state.uploaded_file_name = None # To track if the file has changed by name
        st.session_state.show_generation_section = False # Control visibility of AI generation form
        st.session_state.email_generated = False # New flag to control display of generated email fields
        st.session_state.initialized = True
init_state()

# --- Language Selection (moved up for immediate effect) ---
with st.sidebar:
    chosen_lang = st.selectbox(
        _t("Language"), # Now translated
        options=list(LANGUAGES.keys()),
        format_func=lambda x: LANGUAGES[x], # Display full language name
        index=list(LANGUAGES.keys()).index(st.session_state.language),
        key="language_selector"
    )
    if chosen_lang != st.session_state.language:
        st.session_state.language = chosen_lang
        set_language(chosen_lang)
        st.rerun()

# Apply the selected language immediately after initialization and selection
set_language(st.session_state.language)

# --- UI Helpers ---
def render_step_indicator(current_step: int):
    steps = [_t("1. Generation"), _t("2. Preview"), _t("3. Results")]
    cols = st.columns(len(steps))
    for idx, label in enumerate(steps, start=1):
        text = f"▶ **{label}**" if idx == current_step else label
        with cols[idx-1]:
            st.markdown(f"<p style='text-align: center;'>{text}</p>", unsafe_allow_html=True) # Center align steps

@contextmanager
def card_container():
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    yield
    st.markdown("</div>", unsafe_allow_html=True)

# --- Business Logic ---
def generate_email_preview_and_template():
    st.session_state.generation_in_progress = True
    # Ensure OPENAI_API_KEY is available. config.py should handle this.
    if not OPENAI_API_KEY:
        st.error(_t("OpenAI API Key is not configured. Please set it in Streamlit secrets."))
        st.session_state.generation_in_progress = False
        return

    agent = SmartEmailAgent(openai_api_key=OPENAI_API_KEY)
    
    template = agent.generate_email_template(
        prompt=st.session_state.user_prompt,
        user_email_context=st.session_state.user_email_context,
        output_language=st.session_state.language,
        personalize_emails=st.session_state.personalize_emails
    )
    st.session_state.template_subject = template['subject']
    st.session_state.template_body = template['body']
    st.session_state.editable_subject = template['subject']
    st.session_state.editable_body = template['body']
    st.session_state.generation_in_progress = False
    st.session_state.email_generated = True # Set flag to show generated email fields
    # st.session_state.page = 'preview' # Removed: Stay on 'generate' page to allow regeneration
    st.rerun() # Rerun to display the generated email

def send_all_emails():
    st.session_state.sending_in_progress = True
    status = []
    success = fail = 0
    total_contacts = len(st.session_state.contacts)

    # Initialize a progress bar
    progress_text = _t("Sending emails. Please wait.")
    my_bar = st.progress(0, text=progress_text)

    for i, contact in enumerate(st.session_state.contacts):
        # Update progress bar
        progress_percentage = (i + 1) / total_contacts
        my_bar.progress(progress_percentage, text=f"{progress_text} ({i+1}/{total_contacts})")

        if not contact.get('email'):
            msg = f"Skipped: Contact without email - {contact.get('name', 'N/A')}"
            status.append(msg)
            fail += 1
            continue

        email = contact['email']
        name_for_email = contact.get('name') # Default to None

        # Determine name for email based on personalization setting
        if st.session_state.personalize_emails and name_for_email:
            # If personalization is on and name exists in contact
            pass # Use actual name_for_email
        else:
            # If personalization is off, or name is missing, use generic greeting
            name_for_email = st.session_state.generic_greeting if st.session_state.generic_greeting else _t("Valued Customer")
        
        # Replace placeholders based on personalization setting and available data
        subj = st.session_state.editable_subject
        body = st.session_state.editable_body

        if st.session_state.personalize_emails:
            # Only replace if personalization is active
            subj = subj.replace('{{Name}}', contact.get('name', '')) # Replace with actual name or empty string
            body = body.replace('{{Name}}', contact.get('name', ''))
            
            # Replace {{Email}} placeholder regardless of personalization for dynamic content
            subj = subj.replace('{{Email}}', email)
            body = body.replace('{{Email}}', email)
        else:
            # If not personalizing, replace {{Name}} with generic greeting if it exists in template
            subj = subj.replace('{{Name}}', name_for_email)
            body = body.replace('{{Name}}', name_for_email)
            # Still replace {{Email}} in generic templates if present
            subj = subj.replace('{{Email}}', email)
            body = body.replace('{{Email}}', email)

        # Handle custom fields. This is a simplified example; a robust solution
        # would iterate through contact's properties and template placeholders.
        # For now, let's assume {Custom_Field: Key} format.
        def replace_custom_fields(text_content, contact_data):
            for match in re.finditer(r'\{\{Custom_Field:\s*([^}]+)\}\}', text_content):
                field_key = match.group(1).strip()
                replacement_value = contact_data.get(field_key, f"[{field_key} Not Found]")
                text_content = text_content.replace(match.group(0), str(replacement_value))
            return text_content
        
        body = replace_custom_fields(body, contact)
        subj = replace_custom_fields(subj, contact)


        try:
            result = send_email_message(
                sender_email=SENDER_EMAIL,
                sender_password=SENDER_PASSWORD,
                to_email=email,
                subject=subj,
                body=body,
                attachments=st.session_state.attachments,
                log_path=FAILED_EMAILS_LOG_PATH
            )
            if result.get('status') == 'success':
                msg = f"Success: {name_for_email} <{email}>"
                success += 1
            else:
                msg = f"Error: {name_for_email} <{email}> - {result.get('message')}"
                fail += 1
            status.append(msg)
        except Exception as e:
            msg = f"Error: {name_for_email} <{email}> - {str(e)}"
            status.append(msg)
            fail += 1
    
    my_bar.empty() # Clear the progress bar after completion

    st.session_state.email_sending_status = status
    st.session_state.sending_summary = {
        'total_contacts': total_contacts,
        'successful': success,
        'failed': fail
    }
    st.session_state.page = 'results'
    st.session_state.sending_in_progress = False
    st.rerun()


# --- Page: Generate ---
def page_generate():
    st.subheader(_t("1. Email Generation"))
    render_step_indicator(1)

    # --- Sender Information (Always visible at the top) ---
    st.markdown("---")
    st.markdown(f"**{_t('Sender Email')}:** `{SENDER_EMAIL if SENDER_EMAIL else _t('Not configured')}`")
    if not SENDER_EMAIL or not SENDER_PASSWORD:
        st.warning(_t("Sender email credentials are not configured. Please set SENDER_EMAIL and SENDER_PASSWORD in Streamlit secrets."))
    st.markdown("---")

    # --- File Upload ---
    uploaded_file = st.file_uploader(
        _t("Upload Excel (.xlsx/.xls)"), type=["xlsx","xls"]
    )

    # Process file only if a new file is uploaded (by name or initial upload)
    if uploaded_file is not None and \
       (st.session_state.uploaded_file_name is None or \
        st.session_state.uploaded_file_name != uploaded_file.name):
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp_file:
            shutil.copyfileobj(uploaded_file, tmp_file)
            temp_file_path = tmp_file.name

        contacts, issues = load_contacts_from_excel(temp_file_path)
        st.session_state.contacts = contacts
        st.session_state.contact_issues = issues
        st.session_state.uploaded_file_name = uploaded_file.name
        st.session_state.show_generation_section = True # Show the generation form once file is processed
        st.session_state.email_generated = False # Reset generated email view on new file upload

        os.remove(temp_file_path)
        st.rerun()

    if st.session_state.uploaded_file_name:
        count = len(st.session_state.contacts)
        st.success(_t("Successfully loaded {count} valid contacts.", count=count))
        if st.session_state.contact_issues:
            for issue in st.session_state.contact_issues:
                st.warning(issue)
        
        st.markdown("---") # Visual separator

        # --- AI Email Generation Section (visible after file upload) ---
        if st.session_state.show_generation_section:
            # Personalization checkbox and generic greeting
            st.session_state.personalize_emails = st.checkbox(
                _t("Personalize emails?"), value=st.session_state.personalize_emails, key="personalize_checkbox"
            )
            if not st.session_state.personalize_emails:
                st.session_state.generic_greeting = st.text_input(
                    _t("Generic Greeting (e.g., 'Dear Valued Customer')"), 
                    value=st.session_state.generic_greeting, 
                    placeholder=_t("Enter a generic greeting if not personalizing"), 
                    key="generic_greeting_input"
                )
            else:
                # Clear generic greeting if personalization is re-enabled
                if 'generic_greeting' in st.session_state:
                    st.session_state.generic_greeting = ''

            st.session_state.user_prompt = st.text_area(
                _t("AI Instruction: Describe the email you want to generate."), 
                value=st.session_state.user_prompt, height=150, 
                placeholder=_t("e.g., 'Draft a newsletter about our new product features.'"),
                key="ai_instruction_input"
            )
            st.session_state.user_email_context = st.text_area(
                _t("Email Context (optional): Add style, tone, or specific details."), 
                value=st.session_state.user_email_context, height=100, 
                placeholder=_t("e.g., 'Friendly tone, include a call to action to visit our website.'"),
                key="email_context_input"
            )
            
            if st.button(_t("Generate Email"), use_container_width=True, key="generate_email_button",
                         disabled=st.session_state.generation_in_progress):
                if st.session_state.user_prompt:
                    with st.spinner(_t("Generating email template... Please wait.")):
                        generate_email_preview_and_template()
                else:
                    st.warning(_t("Please provide instructions for the AI to generate the email."))
            
            # Display generated email fields only after generation
            if st.session_state.email_generated:
                st.success(_t("Your email has been generated! You can modify it below."))
                with card_container():
                    st.session_state.editable_subject = st.text_input(
                        _t("Subject"), value=st.session_state.editable_subject, key="generated_subject_input"
                    )
                    st.session_state.editable_body = st.text_area(
                        _t("Body"), value=st.session_state.editable_body, height=350, key="generated_body_input"
                    )
                
                st.markdown("---")
                if st.button(_t("Proceed to Preview & Send"), use_container_width=True, key="proceed_to_preview_button"):
                    st.session_state.page = 'preview'
                    st.rerun()

    else:
        st.info(_t("Please upload an Excel file to get started."))


# --- Page: Preview ---
def page_preview():
    st.subheader(_t("2. Preview & Attachments"))
    render_step_indicator(2)

    col1, col2 = st.columns(2)
    with col1:
        with card_container():
            st.markdown(f"**{_t('Editable Email Content')}**")
            st.session_state.editable_subject = st.text_input(
                _t("Subject"), value=st.session_state.editable_subject, key="preview_subject_input"
            )
            st.session_state.editable_body = st.text_area(
                _t("Body"), value=st.session_state.editable_body, height=400, key="preview_body_input" # Increased height for editing
            )
        
        # Back button
        if st.button(_t("Back to Generation"), use_container_width=True, key="back_to_generate_button"):
            st.session_state.page = 'generate'
            st.rerun()

    with col2:
        with card_container():
            st.markdown(f"**{_t('Live Preview for First Contact')}**")
            if st.session_state.contacts:
                first = st.session_state.contacts[0]
                
                # Determine name for preview based on personalization
                name_for_preview = ""
                if st.session_state.personalize_emails and first.get('name'):
                    name_for_preview = first['name']
                else:
                    name_for_preview = st.session_state.generic_greeting if st.session_state.generic_greeting else _t("Valued Customer")

                email_for_preview = first.get('email', 'example@example.com')
                
                # Replace placeholders for preview
                preview_subj = st.session_state.editable_subject.replace("{{Name}}", name_for_preview).replace("{{Email}}", email_for_preview)
                preview_body = st.session_state.editable_body.replace("{{Name}}", name_for_preview).replace("{{Email}}", email_for_preview)

                # Custom field replacement for preview
                def replace_custom_fields_preview(text_content, contact_data):
                    for match in re.finditer(r'\{\{Custom_Field:\s*([^}]+)\}\}', text_content):
                        field_key = match.group(1).strip()
                        replacement_value = contact_data.get(field_key, f"[{field_key} Not Found]")
                        text_content = text_content.replace(match.group(0), str(replacement_value))
                    return text_content
                
                preview_body = replace_custom_fields_preview(preview_body, first)
                preview_subj = replace_custom_fields_preview(preview_subj, first)

                st.markdown(f"**{_t('Subject')}:** {preview_subj}")
                # Use st.markdown with `unsafe_allow_html=False` (default) for plain text
                # to render newlines correctly. If rich HTML is truly desired, 
                # a more complex rendering is needed.
                st.markdown(preview_body)
            else:
                st.info(_t("Upload contacts in the first step to see a preview."))

    st.markdown("---") # Separator before attachments
    st.subheader(_t("Attachments"))
    files = st.file_uploader(
        _t("Add Attachments"), accept_multiple_files=True, key="attachment_uploader"
    )
    if files:
        st.session_state.attachments = files
        st.info(_t("Attachments selected: {count}", count=len(files)))
        
    if st.session_state.attachments:
        st.markdown(f"**{_t('Current Attachments')}:**")
        for att in st.session_state.attachments:
            st.write(f"- {att.name}")

    st.markdown("---")
    if st.button(_t("Confirm Send"), use_container_width=True, key="confirm_send_button",
                 disabled=st.session_state.sending_in_progress or not st.session_state.contacts):
        if st.session_state.contacts:
            send_all_emails()
        else:
            st.warning(_t("No contacts loaded to send emails to."))


# --- Page: Results ---
def page_results():
    st.subheader(_t("3. Results"))
    render_step_indicator(3)
    
    st.markdown("---")
    total = st.session_state.sending_summary['total_contacts']
    suc = st.session_state.sending_summary['successful']
    fail = st.session_state.sending_summary['failed']

    if total == suc and total > 0:
        st.success(_t("All emails sent successfully!"))
        st.write(_t("All {count} emails were sent without any issues.", count=total))
    elif total > 0:
        st.warning(_t("Sending complete with errors."))
        st.write(_t("Some emails failed to send. Please check the log below for details."))
    else:
        st.info(_t("No emails were processed."))
        
    st.markdown("---")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(_t("Total Contacts"), total)
    with col2:
        st.metric(_t("Emails Successfully Sent"), suc)
    with col3:
        st.metric(_t("Emails Failed to Send"), fail)

    if st.session_state.email_sending_status:
        st.markdown("---")
        with st.expander(_t("Show Activity Log and Errors")):
            log_container = st.container(height=300)
            for log_entry in st.session_state.email_sending_status:
                if "error" in log_entry.lower() or "failed" in log_entry.lower():
                    log_container.error(log_entry)
                elif "success" in log_entry.lower():
                    log_container.success(log_entry)
                else:
                    log_container.info(log_entry)

    st.markdown("---")
    if st.button(_t("Start New Email Session"), use_container_width=True, key="start_new_session_button"):
        # Clear all relevant session state variables
        keys_to_clear = [
            'initialized', 'language', 'page', 'contacts', 'contact_issues', 
            'attachments', 'email_sending_status', 'sending_summary', 
            'generation_in_progress', 'sending_in_progress', 'user_prompt', 
            'user_email_context', 'personalize_emails', 'generic_greeting', 
            'template_subject', 'template_body', 'editable_subject', 'editable_body',
            'uploaded_file_name', 'show_generation_section', 'email_generated'
        ]
        for k in keys_to_clear:
            if k in st.session_state:
                del st.session_state[k]
        init_state() # Re-initialize to default states
        st.rerun() # Force a rerun to restart the app


# --- Main Navigation ---
if st.session_state.page == 'generate':
    page_generate()
elif st.session_state.page == 'preview':
    page_preview()
else: # 'results'
    page_results()