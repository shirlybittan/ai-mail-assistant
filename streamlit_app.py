# streamlit_app.py

import streamlit as st
import pandas as pd
from data_handler import load_contacts_from_excel
from email_agent import SmartEmailAgent # NEW: Use the unified email_agent
from email_tool import send_email_message
from config import SENDER_CREDENTIALS, OPENAI_API_KEY, SENDER_EMAIL, SENDER_PASSWORD, FAILED_EMAILS_LOG_PATH
import tempfile
import os
import shutil
import datetime

# --- IMPORT LANGUAGE HELPER ---
from translations import LANGUAGES, _t, set_language

# --- Streamlit Page Configuration ---
st.set_page_config(layout="wide", page_title=_t("AI Email Assistant"))

# --- Global Variables / Access from config (defined at top scope) ---
selected_sender_email = SENDER_EMAIL
selected_sender_password = SENDER_PASSWORD

# --- Session State Initialization ---
# Ensure language is set BEFORE the selectbox is rendered
if 'language' not in st.session_state:
    st.session_state.language = "fr" # Default language set to French

set_language(st.session_state.language) # Set the global language helper based on session state

if 'page' not in st.session_state:
    st.session_state.page = 'generate' # Initial page

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

# Email generation states
if 'generated_personalized_emails' not in st.session_state:
    st.session_state.generated_personalized_emails = {} # Store personalized emails
if 'template_email' not in st.session_state:
    st.session_state.template_email = None # Store the general template email
if 'personalize_emails' not in st.session_state:
    st.session_state.personalize_emails = True
if 'user_prompt' not in st.session_state:
    st.session_state.user_prompt = ""
if 'user_email_context' not in st.session_state:
    st.session_state.user_email_context = ""
if 'generic_greeting' not in st.session_state:
    st.session_state.generic_greeting = ""
if 'final_emails_to_send' not in st.session_state:
    st.session_state.final_emails_to_send = []

# --- Custom UI Components (from app.py) ---
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# local_css("app.py") # Use this if you save the styles to a separate app.css file


# --- Functions ---
def reset_state():
    """Resets all session state variables for a new session."""
    st.session_state.contacts = []
    st.session_state.contact_issues = []
    st.session_state.uploaded_attachments = []
    st.session_state.email_sending_status = []
    st.session_state.generated_personalized_emails = {}
    st.session_state.template_email = None
    st.session_state.personalize_emails = True
    st.session_state.user_prompt = ""
    st.session_state.user_email_context = ""
    st.session_state.generic_greeting = ""
    st.session_state.page = 'generate'
    st.session_state.final_emails_to_send = []

def generate_email_previews():
    """Generates email previews for all valid contacts."""
    st.session_state.generated_personalized_emails = {} # Clear previous previews
    st.session_state.email_sending_status = [_t("Generating email previews... This may take a moment.")]
    
    agent = SmartEmailAgent(openai_api_key=OPENAI_API_KEY)
    
    # Check if we should generate a template or personalized emails
    if st.session_state.personalize_emails:
        # Generate personalized emails for each contact
        for contact in st.session_state.contacts:
            if contact['email'] not in st.session_state.generated_personalized_emails:
                st.session_state.email_sending_status.append(_t(f"Generating personalized email for {contact['name']} ({contact['email']})..."))
                
                # NEW: Call the unified generate_email method with contact info
                preview = agent.generate_email(
                    prompt=st.session_state.user_prompt,
                    contact_info=contact,
                    user_email_context=st.session_state.user_email_context,
                    output_language=st.session_state.language
                )
                
                if preview["subject"] != "Error":
                    st.session_state.generated_personalized_emails[contact['email']] = preview
                    st.session_state.email_sending_status.append(_t(f"  - Generated email for {contact['name']} successfully."))
                else:
                    st.session_state.email_sending_status.append(_t(f"  - ERROR: Failed to generate email for {contact['name']}. Details: {preview['body']}"))
    else:
        # Generate a single template email
        st.session_state.email_sending_status.append(_t("Generating a general email template..."))
        
        # NEW: Call the unified generate_email method without contact info
        template = agent.generate_email(
            prompt=st.session_state.user_prompt,
            contact_info=None,
            user_email_context=st.session_state.user_email_context,
            output_language=st.session_state.language
        )
        
        if template["subject"] != "Error":
            st.session_state.template_email = template
            st.session_state.email_sending_status.append(_t("  - Generated template email successfully."))
        else:
            st.session_state.email_sending_status.append(_t(f"  - ERROR: Failed to generate template email. Details: {template['body']}"))

    st.session_state.page = 'preview'


# --- UI LAYOUT ---
st.header(_t("AI Email Assistant"))

# Language selection on the sidebar
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
        st.experimental_rerun()
        
    st.markdown("---")
    st.markdown(_t("This app allows you to send mass personalized emails using an AI agent."))


# --- Page Navigation ---
if st.session_state.page == 'generate':
    st.subheader(_t("1. Email Generation"))
    
    # File uploader for contacts
    uploaded_file = st.file_uploader(_t("Upload an Excel file with contacts (.xlsx)"), type=["xlsx", "xls"], key="file_uploader")

    if uploaded_file and uploaded_file.name != st.session_state.get('last_uploaded_file_name'):
        st.session_state.last_uploaded_file_name = uploaded_file.name
        st.session_state.contacts, st.session_state.contact_issues = load_contacts_from_excel(uploaded_file)
        
        if st.session_state.contacts:
            st.success(_t(f"Successfully loaded {len(st.session_state.contacts)} valid contacts."))
        if st.session_state.contact_issues:
            for issue in st.session_state.contact_issues:
                st.warning(issue)
            
        st.experimental_rerun()
    elif 'last_uploaded_file_name' in st.session_state and st.session_state.contacts:
        st.success(_t(f"Using previously loaded contacts: {len(st.session_state.contacts)} valid contacts found."))
        
        # Display issues from previous upload, if any
        if st.session_state.contact_issues:
            st.warning(_t("Some contacts had issues and were skipped."))
            with st.expander(_t("Show skipped contacts")):
                for issue in st.session_state.contact_issues:
                    st.write(f"- {issue}")

    st.markdown("---")
    
    # Email details
    st.session_state.personalize_emails = st.checkbox(_t("Personalize emails for each contact?"), value=st.session_state.personalize_emails, key="personalize_checkbox")
    
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
        st.info(_t(f"You have uploaded {len(st.session_state.uploaded_attachments)} attachments."))
    else:
        st.session_state.uploaded_attachments = []
        
    st.markdown("---")
    
    # Action buttons
    col1, col2 = st.columns(2)
    with col1:
        if st.button(_t("Generate Previews"), use_container_width=True, disabled=not st.session_state.contacts or not st.session_state.user_prompt):
            generate_email_previews()
    with col2:
        if st.button(_t("Start Over"), use_container_width=True):
            reset_state()


elif st.session_state.page == 'preview':
    st.subheader(_t("2. Review and Send Emails"))
    st.info(_t("Review the generated emails below. You can edit the subject and body before sending."))
    
    tab1, tab2 = st.tabs([_t("Email Preview"), _t("Activity Log")])
    
    with tab1:
        st.subheader(_t("Email Preview"))
        if st.session_state.personalize_emails:
            if st.session_state.generated_personalized_emails:
                st.info(_t(f"Showing preview for the first contact. You can modify this template, and the changes will be applied to all other emails."))
                first_contact_email = st.session_state.contacts[0]['email']
                first_email_preview = st.session_state.generated_personalized_emails.get(first_contact_email, {})

                if first_email_preview:
                    # Editable text inputs
                    st.session_state.editable_preview_subject = st.text_input(_t("Subject"), value=first_email_preview.get("subject", ""), key="preview_subject")
                    st.session_state.editable_preview_body = st.text_area(_t("Body"), value=first_email_preview.get("body", ""), height=400, key="preview_body")
        else: # Template-based email
            if st.session_state.template_email:
                st.info(_t("You are sending a general template email. You can edit the subject and body below."))
                
                # Editable text inputs
                st.session_state.editable_preview_subject = st.text_input(_t("Subject"), value=st.session_state.template_email.get("subject", ""), key="template_subject")
                st.session_state.editable_preview_body = st.text_area(_t("Body"), value=st.session_state.template_email.get("body", ""), height=400, key="template_body")
                
                st.session_state.generic_greeting = st.text_input(_t("Generic Greeting Placeholder (e.g., 'Hello there')"), key="generic_greeting_input")

    with tab2:
        st.subheader(_t("Generation Log"))
        log_container = st.container()
        with log_container:
            for log_entry in st.session_state.email_sending_status:
                st.write(log_entry)
        
    st.markdown("---")
    
    # --- Send Emails Action ---
    if st.button(_t("Send All Emails"), use_container_width=True, disabled=st.session_state.sending_in_progress):
        
        # Disable the button to prevent multiple clicks
        st.session_state.sending_in_progress = True
        
        # Prepare the final emails to send
        st.session_state.final_emails_to_send = []
        if st.session_state.personalize_emails:
            # Use the edited subject and body as the new template for personalized emails
            template_subject = st.session_state.editable_preview_subject
            template_body = st.session_state.editable_preview_body
            
            # Apply the edits to the personalized emails
            for contact in st.session_state.contacts:
                personalized_email = st.session_state.generated_personalized_emails.get(contact['email'], {})
                if personalized_email:
                    # Create the final email by replacing placeholders in the edited template
                    final_subject = template_subject.replace("{{Name}}", contact.get('name', ''))
                    final_body = template_body.replace("{{Name}}", contact.get('name', ''))
                    final_body = final_body.replace("{{Email}}", contact.get('email', ''))
                    
                    st.session_state.final_emails_to_send.append({
                        "recipient_email": contact['email'],
                        "recipient_name": contact['name'],
                        "subject": final_subject,
                        "body": final_body,
                        "attachments": st.session_state.uploaded_attachments
                    })
        else: # Template-based sending
            template_subject = st.session_state.editable_preview_subject
            template_body = st.session_state.editable_preview_body
            
            # Use the template for all contacts
            for contact in st.session_state.contacts:
                # Replace the generic greeting placeholder if it's set
                if st.session_state.generic_greeting:
                    final_body = template_body.replace("{{Name}}", st.session_state.generic_greeting)
                else:
                    final_body = template_body.replace("{{Name}}", contact.get('name', ''))
                
                st.session_state.final_emails_to_send.append({
                    "recipient_email": contact['email'],
                    "recipient_name": contact['name'],
                    "subject": template_subject,
                    "body": final_body,
                    "attachments": st.session_state.uploaded_attachments
                })

        
        # Proceed with sending emails
        st.session_state.email_sending_status.append(_t("Email sending process initiated..."))
        
        # Use a temporary directory for attachments
        temp_dir = tempfile.mkdtemp()
        attachment_paths = []
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
                
                status_msg = _t(f"--- [{i+1}/{total_emails}] Processing contact: {recipient_name} ({recipient_email}) ---")
                st.session_state.email_sending_status.append(status_msg)
                
                st.session_state.email_sending_status.append(_t(f"  Attempting Email for {recipient_name}..."))
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
                    st.session_state.email_sending_status.append(_t(f"    - Email: success - Email sent to {recipient_email} successfully."))
                else:
                    st.session_state.email_sending_status.append(_t(f"    - Email: error - Failed to send to {recipient_email}. Details: {result['message']}"))
            
            st.session_state.email_sending_status.append(_t("--- Email sending process complete ---"))
            
        finally:
            st.session_state.sending_in_progress = False
            # Clean up temporary directory
            try:
                if os.path.exists(temp_dir):
                    shutil.rmtree(temp_dir)
            except Exception as cleanup_e:
                st.session_state.email_sending_status.append(f"{_t('ERROR: Could not clean up temporary attachments: ')}{cleanup_e}")
                print(f"ERROR: streamlit_app.py: Could not clean up temporary directory {temp_dir}: {cleanup_e}")

        # Final display of the complete log
        st.empty().write("".join(st.session_state.email_sending_status))

    if not st.session_state.sending_in_progress: # Only show 'Start New' button when sending is done
        if st.button(_t("Start New Email Session"), use_container_width=True):
            # Reset all relevant session state variables for a fresh start
            reset_state()
            st.experimental_rerun()