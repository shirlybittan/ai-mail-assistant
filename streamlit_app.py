# streamlit_app.py

import streamlit as st
import pandas as pd
from data_handler import load_contacts_from_excel
from email_agent import SmartEmailAgent # Updated import
from email_tool import send_email_message
from config import SENDER_CREDENTIALS, OPENAI_API_KEY, SENDER_EMAIL, SENDER_PASSWORD, FAILED_EMAILS_LOG_PATH
import tempfile
import os
import shutil
import datetime
import re

# --- IMPORT LANGUAGE HELPER ---
from translations import LANGUAGES, _t, set_language

# --- Streamlit Page Configuration ---
st.set_page_config(layout="wide", page_title=_t("AI Email Assistant"))

# --- Global Variables / Access from config (defined at top scope) ---
selected_sender_email = SENDER_EMAIL
selected_sender_password = SENDER_PASSWORD

# --- Session State Initialization ---
if 'language' not in st.session_state:
    st.session_state.language = "fr"
set_language(st.session_state.language)

if 'page' not in st.session_state:
    st.session_state.page = 'generate'

# Core data states
if 'contacts' not in st.session_state:
    st.session_state.contacts = []
if 'contact_issues' not in st.session_state:
    st.session_state.contact_issues = []
if 'uploaded_attachments' not in st.session_state:
    st.session_state.uploaded_attachments = []
if 'email_sending_status' not in st.session_state:
    st.session_state.email_sending_status = []
if 'sending_in_progress' not in st.session_state:
    st.session_state.sending_in_progress = False
if 'file_uploader_key' not in st.session_state:
    st.session_state.file_uploader_key = 0
if 'last_uploaded_file_name' not in st.session_state:
    st.session_state.last_uploaded_file_name = None

# Email generation states
if 'personalize_emails' not in st.session_state:
    st.session_state.personalize_emails = False
if 'template_email' not in st.session_state:
    st.session_state.template_email = None
if 'user_prompt' not in st.session_state:
    st.session_state.user_prompt = ""
if 'user_email_context' not in st.session_state:
    st.session_state.user_email_context = ""
if 'generic_greeting' not in st.session_state:
    st.session_state.generic_greeting = ""
if 'final_emails_to_send' not in st.session_state:
    st.session_state.final_emails_to_send = []

# Sending results state
if 'sending_summary' not in st.session_state:
    st.session_state.sending_summary = {
        'total_contacts': 0,
        'successful': 0,
        'failed': 0
    }
if 'generation_in_progress' not in st.session_state:
    st.session_state.generation_in_progress = False

# --- Functions ---
def reset_state():
    """Resets all session state variables for a new session."""
    st.session_state.contacts = []
    st.session_state.contact_issues = []
    st.session_state.uploaded_attachments = []
    st.session_state.email_sending_status = []
    st.session_state.template_email = None
    st.session_state.personalize_emails = False
    st.session_state.user_prompt = ""
    st.session_state.user_email_context = ""
    st.session_state.generic_greeting = ""
    st.session_state.page = 'generate'
    st.session_state.final_emails_to_send = []
    st.session_state.sending_summary = {
        'total_contacts': 0,
        'successful': 0,
        'failed': 0
    }
    st.session_state.file_uploader_key += 1
    st.session_state.last_uploaded_file_name = None
    st.session_state.generation_in_progress = False


def generate_email_preview_and_template():
    """
    Generates a single email template with placeholders.
    """
    st.session_state.generation_in_progress = True
    st.session_state.template_email = None
    st.session_state.email_sending_status = [_t("Generating email template... This may take a moment.")]

    # Create an agent instance
    agent = SmartEmailAgent(openai_api_key=OPENAI_API_KEY)

    # Call the agent's template generation method once
    template = agent.generate_email_template(
        prompt=st.session_state.user_prompt,
        user_email_context=st.session_state.user_email_context,
        output_language=st.session_state.language
    )

    if template["subject"] != "Error":
        st.session_state.template_email = template
        st.session_state.email_sending_status.append(_t("  - Generated template email successfully."))
        
        # We store the template directly
        st.session_state.template_email['preview_subject'] = template['subject']
        st.session_state.template_email['preview_body'] = template['body']
    else:
        st.session_state.email_sending_status.append(_t("  - ERROR: Failed to generate template email. Details: {details}", details=template['body']))

    st.session_state.generation_in_progress = False
    st.session_state.page = 'preview'


# --- UI LAYOUT ---
st.header(_t("AI Email Assistant"))

with st.sidebar:
    st.header(_t("Settings"))
    
    selected_language = st.selectbox(
        _t("Select your language"),
        options=list(LANGUAGES.keys()),
        format_func=lambda x: LANGUAGES[x],
        index=list(LANGUAGES.keys()).index(st.session_state.language),
        key="lang_selectbox"
    )
    if st.session_state.language != selected_language:
        st.session_state.language = selected_language
        set_language(st.session_state.language)
        st.rerun()
        
    st.markdown("---")
    st.markdown(_t("This app allows you to send mass personalized emails using an AI agent."))


# --- Page Navigation Logic ---
if st.session_state.page == 'generate':
    st.subheader(_t("1. Email Generation"))
    
    uploaded_file = st.file_uploader(
        _t("Upload an Excel file with contacts (.xlsx)"),
        type=["xlsx", "xls"],
        key=f"file_uploader_{st.session_state.file_uploader_key}"
    )

    if uploaded_file and uploaded_file.name != st.session_state.get('last_uploaded_file_name'):
        st.session_state.last_uploaded_file_name = uploaded_file.name
        st.session_state.contacts, st.session_state.contact_issues = load_contacts_from_excel(uploaded_file)
        
        if st.session_state.contacts:
            st.success(_t("Successfully loaded {count} valid contacts.", count=len(st.session_state.contacts)))
        if st.session_state.contact_issues:
            for issue in st.session_state.contact_issues:
                st.warning(issue)
            
        st.rerun()
    elif 'last_uploaded_file_name' in st.session_state and st.session_state.contacts:
        st.success(_t("Using previously loaded contacts: {count} valid contacts found.", count=len(st.session_state.contacts)))
        
        if st.session_state.contact_issues:
            st.warning(_t("Some contacts had issues and were skipped."))
            with st.expander(_t("Show skipped contacts")):
                for issue in st.session_state.contact_issues:
                    st.write(f"- {issue}")

    st.markdown("---")
    
    st.session_state.personalize_emails = st.checkbox(
        _t("Personalize emails for each contact?"),
        value=st.session_state.personalize_emails,
        key="personalize_checkbox"
    )
    
    if not st.session_state.personalize_emails:
        st.session_state.generic_greeting = st.text_input(
            _t("Generic Greeting Placeholder (e.g., 'Dear Friends')"),
            value=st.session_state.generic_greeting,
            key="generic_greeting_input"
        )
    
    st.write(_t("Enter your instruction for the AI agent:"))
    st.session_state.user_prompt = st.text_area(
        _t("AI Instruction"),
        value=st.session_state.user_prompt,
        placeholder=_t("e.g., 'Write a follow-up email to customers who purchased our new product. Thank them and offer a discount on their next purchase.'"),
        height=150,
        key="prompt_area"
    )

    st.write(_t("Additional context for the email (optional):"))
    st.session_state.user_email_context = st.text_area(
        _t("Email Context"),
        value=st.session_state.user_email_context,
        placeholder=_t("e.g., 'Keep the tone professional but friendly.'"),
        height=100,
        key="context_area"
    )
    
    st.markdown("---")
    
    st.subheader(_t("Attachments (Optional)"))
    uploaded_attachments = st.file_uploader(_t("Upload files to attach to all emails"), type=None, accept_multiple_files=True, key="attachment_uploader")
    
    if uploaded_attachments:
        st.session_state.uploaded_attachments = uploaded_attachments
        st.info(_t("You have uploaded {count} attachments.", count=len(st.session_state.uploaded_attachments)))
    else:
        st.session_state.uploaded_attachments = []
        
    st.markdown("---")
    
    generate_button_disabled = not st.session_state.contacts or not st.session_state.user_prompt or st.session_state.generation_in_progress
    if st.button(_t("Generate Previews"), use_container_width=True, disabled=generate_button_disabled):
        with st.spinner(_t("Generating email... please wait")):
            generate_email_preview_and_template()


elif st.session_state.page == 'preview':
    st.subheader(_t("2. Review and Send Emails"))
    st.info(_t("Review the generated email template below. You can edit the subject and body before sending."))
    
    tab1, tab2 = st.tabs([_t("Email Preview"), _t("Activity Log")])
    
    with tab1:
        st.subheader(_t("Email Preview"))
        if st.session_state.template_email:
            st.session_state.editable_preview_subject = st.text_input(
                _t("Subject"),
                value=st.session_state.template_email.get("subject", ""),
                key="preview_subject"
            )
            st.session_state.editable_preview_body = st.text_area(
                _t("Body"),
                value=st.session_state.template_email.get("body", ""),
                height=400,
                key="preview_body"
            )

    with tab2:
        st.subheader(_t("Generation Log"))
        log_container = st.container()
        with log_container:
            for log_entry in st.session_state.email_sending_status:
                st.write(log_entry)
        
    st.markdown("---")
    
    if st.button(_t("Send All Emails"), use_container_width=True, disabled=st.session_state.sending_in_progress):
        st.session_state.sending_in_progress = True
        
        template_subject = st.session_state.editable_preview_subject
        template_body = st.session_state.editable_preview_body
        
        st.session_state.final_emails_to_send = []
        with st.spinner(_t("Preparing emails for sending...")):
            for contact in st.session_state.contacts:
                recipient_name = contact.get('name', 'Contact')
                recipient_email = contact['email']
                
                final_subject = template_subject
                final_body = template_body
                
                if st.session_state.personalize_emails:
                    final_subject = final_subject.replace("{{Name}}", recipient_name)
                    final_body = final_body.replace("{{Name}}", recipient_name)
                elif st.session_state.generic_greeting:
                    final_subject = final_subject.replace("{{Name}}", st.session_state.generic_greeting)
                    final_body = final_body.replace("{{Name}}", st.session_state.generic_greeting)
                
                final_subject = final_subject.replace("{{Email}}", recipient_email)
                final_body = final_body.replace("{{Email}}", recipient_email)
                
                st.session_state.final_emails_to_send.append({
                    "recipient_email": recipient_email,
                    "recipient_name": recipient_name,
                    "subject": final_subject,
                    "body": final_body,
                    "attachments": st.session_state.uploaded_attachments
                })
        
        st.session_state.email_sending_status.append(_t("Email sending process initiated..."))
        
        temp_dir = tempfile.mkdtemp()
        attachment_paths = []
        total_success = 0
        total_failed = 0
        
        try:
            for uploaded_file in st.session_state.uploaded_attachments:
                file_path = os.path.join(temp_dir, uploaded_file.name)
                with open(file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                attachment_paths.append(file_path)
            
            total_emails = len(st.session_state.final_emails_to_send)
            
            for i, email_data in enumerate(st.session_state.final_emails_to_send):
                recipient_email = email_data['recipient_email']
                recipient_name = email_data['recipient_name']
                subject = email_data['subject']
                body = email_data['body']
                
                status_msg = _t("--- [{current}/{total}] Processing contact: {name} ({email}) ---",
                                current=i+1, total=total_emails, name=recipient_name, email=recipient_email)
                st.session_state.email_sending_status.append(status_msg)
                
                st.session_state.email_sending_status.append(_t("  Attempting Email for {name}...", name=recipient_name))
                result = send_email_message(
                    sender_email=selected_sender_email,
                    sender_password=selected_sender_password,
                    to_email=recipient_email,
                    subject=subject,
                    body=body,
                    attachments=attachment_paths,
                    log_path=FAILED_EMAILS_LOG_PATH
                )

                if result['status'] == 'success':
                    st.session_state.email_sending_status.append(_t("    - Email: success - Email sent to {email} successfully.", email=recipient_email))
                    total_success += 1
                else:
                    st.session_state.email_sending_status.append(_t("    - Email: error - Failed to send to {email}. Details: {details}", email=recipient_email, details=result['message']))
                    total_failed += 1
            
            st.session_state.email_sending_status.append(_t("--- Email sending process complete ---"))
            
        finally:
            st.session_state.sending_in_progress = False
            try:
                if os.path.exists(temp_dir):
                    shutil.rmtree(temp_dir)
            except Exception as cleanup_e:
                st.session_state.email_sending_status.append(_t("ERROR: Could not clean up temporary attachments: ") + str(cleanup_e))
                print(f"ERROR: streamlit_app.py: Could not clean up temporary directory {temp_dir}: {cleanup_e}")

        st.session_state.sending_summary = {
            'total_contacts': len(st.session_state.contacts),
            'successful': total_success,
            'failed': total_failed
        }
        st.session_state.page = 'results'
        st.rerun()


elif st.session_state.page == 'results':
    st.subheader(_t("3. Sending Results"))
    
    with st.container():
        cols = st.columns(3)
        with cols[1]:
            if st.button(_t("Start New Email Session"), use_container_width=True):
                reset_state()
                st.rerun()
        
        st.markdown("---")
        
        st.success(_t("Sending complete"))
        st.write(_t("All emails have been sent or an attempt has been made for each contact."))
        
        st.markdown("---")
        
        st.subheader(_t("Summary"))
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(_t("Total Contacts"), st.session_state.sending_summary['total_contacts'])
        with col2:
            st.metric(_t("Emails Successfully Sent"), st.session_state.sending_summary['successful'])
        with col3:
            st.metric(_t("Emails Failed to Send"), st.session_state.sending_summary['failed'])

        failed_emails_log = [log for log in st.session_state.email_sending_status if 'error' in log.lower() or 'failed' in log.lower()]

        if failed_emails_log:
            st.markdown("---")
            with st.expander(_t("Show logs for failed emails")):
                for log_entry in failed_emails_log:
                    st.write(log_entry)