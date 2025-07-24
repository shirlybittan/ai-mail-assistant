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
    st.session_state.personalize_emails = True # Default to personalized
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
# State for editable template
if 'editable_preview_subject' not in st.session_state:
    st.session_state.editable_preview_subject = ""
if 'editable_preview_body' not in st.session_state:
    st.session_state.editable_preview_body = ""
# UI state for preview page
if 'show_live_preview' not in st.session_state:
    st.session_state.show_live_preview = False


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
    st.session_state.personalize_emails = True
    st.session_state.user_prompt = ""
    st.session_state.user_email_context = ""
    st.session_state.generic_greeting = ""
    st.session_state.editable_preview_subject = ""
    st.session_state.editable_preview_body = ""
    st.session_state.show_live_preview = False
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
    
    status_placeholder = st.empty()
    status_placeholder.info(_t("Generating email template... This may take a moment."))
    
    agent = SmartEmailAgent(openai_api_key=OPENAI_API_KEY)

    template = agent.generate_email_template(
        prompt=st.session_state.user_prompt,
        user_email_context=st.session_state.user_email_context,
        output_language=st.session_state.language
    )

    if template.get("subject") and "Error" not in template.get("subject"):
        st.session_state.template_email = template
        # Also update the editable fields
        st.session_state.editable_preview_subject = template.get("subject", "")
        st.session_state.editable_preview_body = template.get("body", "")
        status_placeholder.success(_t("Template email generated successfully!"))
        
    else:
        status_placeholder.error(_t("ERROR: Failed to generate template email. Details: {details}", details=template.get("body", "N/A")))

    st.session_state.generation_in_progress = False


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
    
    generate_button_disabled = not st.session_state.contacts or not st.session_state.user_prompt or st.session_state.generation_in_progress
    if st.button(_t("Generate Email"), use_container_width=True, disabled=generate_button_disabled):
        generate_email_preview_and_template()

    if st.session_state.template_email:
        st.markdown("---")
        st.subheader(_t("Generated Email Template"))
        st.session_state.editable_preview_subject = st.text_input(
            _t("Subject"),
            value=st.session_state.editable_preview_subject,
            key="preview_subject"
        )
        st.session_state.editable_preview_body = st.text_area(
            _t("Body"),
            value=st.session_state.editable_preview_body,
            height=400,
            key="preview_body"
        )

        st.markdown("---")
        if st.button(_t("Proceed to Preview"), use_container_width=True):
            st.session_state.page = 'preview'
            # When proceeding, hide the preview by default on the next page
            st.session_state.show_live_preview = False
            st.rerun()


elif st.session_state.page == 'preview':
    st.subheader(_t("2. Aperçu et envoi"))
    st.info(_t("Review and edit the generated email template below. Click the preview button to see how it looks for the first contact."))

    if st.session_state.template_email and st.session_state.contacts:
        
        # --- REWORK: EDITABLE TEMPLATE FIRST ---
        st.subheader(_t("Edit Template"))
        
        st.session_state.editable_preview_subject = st.text_input(
            _t("Preview Subject"),
            value=st.session_state.editable_preview_subject,
            key="preview_subject_page_2"
        )
        st.session_state.editable_preview_body = st.text_area(
            _t("Preview Body"),
            value=st.session_state.editable_preview_body,
            height=300,
            key="preview_body_page_2"
        )
        
        # --- REWORK: ON-DEMAND PREVIEW BUTTON ---
        if st.button(_t("Show/Update Preview"), use_container_width=True):
            st.session_state.show_live_preview = True

        # --- REWORK: CONDITIONAL PREVIEW DISPLAY ---
        if st.session_state.show_live_preview:
            st.subheader(_t("Live Preview (Example for First Contact)"))
            
            first_contact = st.session_state.contacts[0]
            preview_subject = st.session_state.editable_preview_subject
            preview_body = st.session_state.editable_preview_body

            if st.session_state.personalize_emails:
                recipient_name = first_contact.get('name', 'Contact')
                preview_subject = preview_subject.replace("{{Name}}", recipient_name)
                preview_body = preview_body.replace("{{Name}}", recipient_name)
            elif st.session_state.generic_greeting:
                preview_subject = preview_subject.replace("{{Name}}", st.session_state.generic_greeting)
                preview_body = preview_body.replace("{{Name}}", st.session_state.generic_greeting)
            
            # Robust newline replacement for display
            preview_body_html = preview_body.replace('\r\n', '<br>').replace('\n', '<br>')

            with st.container(border=True):
                st.markdown(f"**{_t('Subject')}:** {preview_subject}")
                st.markdown("---")
                st.markdown(preview_body_html, unsafe_allow_html=True)
        
        st.markdown("---")
        
        st.subheader(_t("Attachments (Optional)"))
        uploaded_attachments = st.file_uploader(_t("Upload files to attach to all emails"), type=None, accept_multiple_files=True, key="attachment_uploader")
        
        if uploaded_attachments:
            st.session_state.uploaded_attachments = uploaded_attachments
            st.info(_t("You have uploaded {count} attachments.", count=len(st.session_state.uploaded_attachments)))
        else:
            st.info(_t("No attachments uploaded."))
    
    st.markdown("---")
    
    if st.button(_t("Confirm Send"), use_container_width=True, disabled=st.session_state.sending_in_progress):
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

                # --- FIX: Robustly convert all newline types to <br> for HTML email ---
                final_body_html = final_body.replace('\r\n', '<br>').replace('\n', '<br>')
                
                st.session_state.final_emails_to_send.append({
                    "recipient_email": recipient_email,
                    "recipient_name": recipient_name,
                    "subject": final_subject,
                    "body": final_body_html, # Send the HTML version
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
    st.subheader(_t("3. Résultats d'envoi"))
    
    with st.container():
        if st.button(_t("Start New Email Session"), use_container_width=True):
            reset_state()
            st.rerun()
        
        st.markdown("---")
        
        if st.session_state.sending_summary['failed'] == 0 and st.session_state.sending_summary['successful'] > 0:
            st.success(_t("All emails sent successfully!"))
            st.write(_t("All {count} emails were sent without any issues.", count=st.session_state.sending_summary['total_contacts']))
        else:
            st.warning(_t("Sending complete with errors."))
            st.write(_t("Some emails failed to send. Please check the log below for details."))
        
        st.markdown("---")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(_t("Total Contacts"), st.session_state.sending_summary['total_contacts'])
        with col2:
            st.metric(_t("Emails Successfully Sent"), st.session_state.sending_summary['successful'])
        with col3:
            st.metric(_t("Emails Failed to Send"), st.session_state.sending_summary['failed'])

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
                        log_container.write(log_entry)