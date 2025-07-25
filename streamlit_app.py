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
if 'generated_subject' not in st.session_state:
    st.session_state.generated_subject = ""
if 'generated_body' not in st.session_state:
    st.session_state.generated_body = ""
if 'email_sending_status' not in st.session_state:
    st.session_state.email_sending_status = [] # To store logs during sending
if 'sending_summary' not in st.session_state:
    st.session_state.sending_summary = {'total_contacts':0, 'successful':0, 'failed':0}
if 'uploaded_file' not in st.session_state:
    st.session_state.uploaded_file = None # To store the uploaded file object itself

# --- AI Agent Initialization ---
try:
    agent = SmartEmailAgent(openai_api_key=OPENAI_API_KEY)
except ValueError as e:
    st.error(f"Configuration Error: {e}. Please ensure OPENAI_API_KEY is set in your Streamlit secrets.")
    st.stop() # Stop the app if API key is missing

# --- Helper Functions ---

# Function to log activity for display in the app
def log_activity(message, is_error=False, is_success=False):
    # Determine the log type for display
    if is_error:
        log_type = "ERROR"
    elif is_success:
        log_type = "SUCCESS"
    else:
        log_type = "INFO"
    st.session_state.email_sending_status.append(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] {log_type}: {message}")

# Function to clear all session state variables
def clear_session_state():
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    # Reinitialize language after clearing to prevent immediate error
    st.session_state.language = "fr" # Default to French
    set_language(st.session_state.language) # Ensure translation system is ready
    log_activity(_t("Session state cleared."))
    st.rerun() # Use st.rerun() to force a complete re-render

def generate_email_content():
    prompt = st.session_state.user_prompt
    user_context = st.session_state.user_context
    output_lang = st.session_state.language # Use selected language for AI generation

    log_activity(_t("Generating email content..."))
    try:
        email_output = agent.generate_email_template(prompt, user_context, output_lang)
        st.session_state.generated_subject = email_output['subject']
        st.session_state.generated_body = email_output['body']
        log_activity(_t("Email content generated successfully."), is_success=True)
    except Exception as e:
        log_activity(_t("Error generating email: {error_message}").format(error_message=e), is_error=True)
        st.error(_t("Error generating email. Please try again."))

def send_all_emails():
    if not st.session_state.contacts:
        st.warning(_t("No contacts loaded. Please upload a contact list first."))
        return
    if not st.session_state.generated_subject or not st.session_state.generated_body:
        st.warning(_t("Email subject or body is empty. Please generate email content first."))
        return

    st.session_state.email_sending_status = [] # Clear previous logs
    st.session_state.sending_summary = {'total_contacts': len(st.session_state.contacts), 'successful': 0, 'failed': 0}
    
    log_activity(_t("Email sending process initiated..."))

    # Create a temporary directory for attachments during sending
    temp_dir = None
    if st.session_state.uploaded_attachments:
        temp_dir = tempfile.mkdtemp()
        log_activity(_t(f"Temporary directory created for attachments: {temp_dir}"))

    try:
        # Prepare actual file paths for attachments
        attachment_paths = []
        for uploaded_attachment in st.session_state.uploaded_attachments:
            if temp_dir:
                # Assuming uploaded_attachment is a BytesIO object (from FileUploader)
                # or a path if it was already saved
                if hasattr(uploaded_attachment, 'read'): # It's a BytesIO object
                    # Create a temporary file and write the content
                    temp_file_path = os.path.join(temp_dir, uploaded_attachment.name)
                    with open(temp_file_path, "wb") as f:
                        f.write(uploaded_attachment.read())
                    attachment_paths.append(temp_file_path)
                elif isinstance(uploaded_attachment, str) and os.path.exists(uploaded_attachment):
                    # It's already a path (e.g., from a previous session state, though unlikely)
                    attachment_paths.append(uploaded_attachment)
                else:
                    log_activity(_t(f"Skipping invalid attachment: {uploaded_attachment}"), is_error=True)
            else: # If no temp_dir was created, implies no valid attachments were uploaded
                pass # No need to log, it's handled by the `if temp_dir:` above


        for i, contact in enumerate(st.session_state.contacts):
            recipient_name = contact.get("name", _t("Contact {index}").format(index=i+1))
            recipient_email = contact.get("email", "")

            if not recipient_email:
                log_activity(_t(f"Skipping contact {recipient_name} due to missing email."), is_error=True)
                st.session_state.sending_summary['failed'] += 1
                continue

            log_activity(_t("--- [{current_num}/{total_num}] Processing contact: {name} ({email}) ---").format(
                current_num=i + 1, total_num=len(st.session_state.contacts), name=recipient_name, email=recipient_email
            ))

            personalized_subject = st.session_state.generated_subject
            personalized_body = st.session_state.generated_body

            # Personalize subject and body if personalization is enabled
            if st.session_state.personalize_email:
                log_activity(_t(f"Generating personalized email for {recipient_name}..."))
                try:
                    # Replace placeholders in subject and body
                    personalized_subject = personalized_subject.replace("{{Name}}", recipient_name)
                    personalized_subject = personalized_subject.replace("{{Email}}", recipient_email)
                    
                    personalized_body = personalized_body.replace("{{Name}}", recipient_name)
                    personalized_body = personalized_body.replace("{{Email}}", recipient_email)

                    # Further AI personalization if needed (this would be a separate agent call)
                    # For now, just placeholder replacement

                except Exception as e:
                    log_activity(_t(f"Error personalizing email for {recipient_name}: {e}"), is_error=True)
                    # Proceed with unpersonalized email if personalization fails
            
            log_activity(_t(f"Attempting Email for {recipient_name}..."))
            
            # Send the email
            send_result = send_email_message(
                sender_email=selected_sender_email,
                sender_password=selected_sender_password,
                to_email=recipient_email,
                subject=personalized_subject,
                body=personalized_body,
                log_path=FAILED_EMAILS_LOG_PATH,
                attachments=attachment_paths # Pass the list of paths
            )

            if send_result['status'] == 'success':
                st.session_state.sending_summary['successful'] += 1
                log_activity(_t("Email sent to {recipient_email} successfully.").format(recipient_email=recipient_email), is_success=True)
            else:
                st.session_state.sending_summary['failed'] += 1
                log_activity(_t("Failed to send to {recipient_email}. Details: {message}").format(
                    recipient_email=recipient_email, message=send_result['message']
                ), is_error=True)
                
    except Exception as e:
        log_activity(_t(f"An unexpected error occurred during email sending: {e}"), is_error=True)
    finally:
        log_activity(_t("--- Email sending process complete ---"))
        log_activity(_t("Summary: {successful_count} successful, {failed_count} failed/skipped.").format(
            successful_count=st.session_state.sending_summary['successful'],
            failed_count=st.session_state.sending_summary['failed']
        ))
        st.session_state.page = 'results' # Navigate to results page
        if temp_dir and os.path.exists(temp_dir):
            try:
                shutil.rmtree(temp_dir)
                log_activity(_t(f"Temporary directory deleted: {temp_dir}"))
            except OSError as e:
                log_activity(_t(f"Error deleting temporary directory {temp_dir}: {e}"), is_error=True)
        st.rerun() # Rerun to show the results page

# --- UI Components ---

# Function to render step indicators
def render_step_indicator(current_step):
    steps = {
        1: _t("1. Email Generation"),
        2: _t("2. Review & Send"),
        3: _t("3. Results")
    }
    cols = st.columns(len(steps))
    for i, (step_num, step_title) in enumerate(steps.items()):
        with cols[i]:
            if step_num == current_step:
                st.markdown(f"**<span style='color: #007bff;'>{step_title}</span>**", unsafe_allow_html=True)
            else:
                st.markdown(f"<span style='color: #6c757d;'>{step_title}</span>", unsafe_allow_html=True)
    st.markdown("---")


# --- Page: Generate Email ---
def page_generate():
    st.subheader(_t("1. Email Generation"))
    render_step_indicator(1)

    st.write(_t("Compose your email details below."))

    # Sender Email (from secrets)
    if selected_sender_email:
        st.info(_t("Sender Email: {email} (Configured in secrets)").format(email=selected_sender_email))
    else:
        st.warning(_t("Sender email is not configured. Please set SENDER_EMAIL and SENDER_PASSWORD in your Streamlit secrets."))

    # File Uploader for Contacts
    st.markdown("---")
    st.markdown(f"**{_t('Upload an Excel file with contacts (.xlsx)')}**")
    uploaded_file = st.file_uploader(
        _t("Drag and drop file here"),
        type=["xlsx", "xls"],
        accept_multiple_files=False,
        key="excel_uploader"
    )

    if uploaded_file is not None and uploaded_file != st.session_state.uploaded_file:
        st.session_state.uploaded_file = uploaded_file # Store the uploaded file object
        
        # Save the uploaded file to a temporary location
        with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            excel_file_path = tmp_file.name

        contacts, issues = load_contacts_from_excel(excel_file_path)
        st.session_state.contacts = contacts
        st.session_state.contact_issues = issues
        
        # Clean up the temporary file
        try:
            os.unlink(excel_file_path)
            log_activity(_t(f"Temporary Excel file deleted: {excel_file_path}"))
        except OSError as e:
            log_activity(_t(f"Error deleting temporary Excel file {excel_file_path}: {e}"), is_error=True)

        if st.session_state.contacts:
            st.success(_t("Successfully loaded {count} valid contacts.").format(count=len(st.session_state.contacts)))
            if st.session_state.contact_issues:
                st.warning(_t("WARNING: Some contacts had issues (e.g., missing/invalid/duplicate emails). They will be skipped."))
                with st.expander(_t("Show Contact Issues")):
                    for issue in st.session_state.contact_issues:
                        st.error(issue)
        elif st.session_state.contact_issues:
            st.error(_t("No valid contacts loaded. Please check the issues below."))
            with st.expander(_t("Show Contact Issues")):
                for issue in st.session_state.contact_issues:
                    st.error(issue)
        else:
            st.info(_t("No contacts found in the uploaded file or file was empty."))

    st.markdown("---")

    # Email Generation Form
    with st.form("email_generation_form"):
        st.session_state.user_prompt = st.text_area(
            _t("What kind of email do you want to generate?"),
            value=st.session_state.get('user_prompt', ""),
            height=150,
            placeholder=_t("e.g., 'A welcome email for new customers, offering a 10% discount.'")
        )
        st.session_state.user_context = st.text_area(
            _t("Any specific style, tone, or information to include?"),
            value=st.session_state.get('user_context', ""),
            height=100,
            placeholder=_t("e.g., 'Formal tone, mention our website: example.com. Use placeholders for Name and Email.'")
        )
        submitted = st.form_submit_button(_t("Generate Email"))
        if submitted:
            if not st.session_state.user_prompt:
                st.error(_t("Please provide a prompt to generate the email."))
            else:
                generate_email_content()

    if st.session_state.generated_subject or st.session_state.generated_body:
        st.markdown("---")
        st.success(_t("Your email has been generated! You can edit it below."))
        st.session_state.generated_subject = st.text_input(
            _t("Subject"), value=st.session_state.generated_subject, key="subject_input"
        )
        st.session_state.generated_body = st.text_area(
            _t("Body"), value=st.session_state.generated_body, height=300, key="body_input"
        )
        
        # Attachment Uploader
        st.markdown("---")
        st.markdown(f"**{_t('Attach files (optional)')}**")
        uploaded_files_attachments = st.file_uploader(
            _t("Drag and drop files here"),
            type=["pdf", "docx", "jpg", "png"], # Add more types as needed
            accept_multiple_files=True,
            key="attachments_uploader"
        )

        # Handle new attachment uploads
        if uploaded_files_attachments:
            for file in uploaded_files_attachments:
                # To prevent duplicate uploads if rerun happens
                if file.name not in [f.name for f in st.session_state.uploaded_attachments]:
                    st.session_state.uploaded_attachments.append(file)
        
        # Display current attachments and allow removal
        if st.session_state.uploaded_attachments:
            st.markdown(_t("Currently attached files:"))
            for i, att_file in enumerate(st.session_state.uploaded_attachments):
                col1, col2 = st.columns([0.8, 0.2])
                with col1:
                    st.write(att_file.name)
                with col2:
                    if st.button(_t("Remove"), key=f"remove_att_{i}"):
                        st.session_state.uploaded_attachments.pop(i)
                        st.rerun() # Rerun to update the list of attachments displayed

            if st.button(_t("Clear All Attachments")):
                st.session_state.uploaded_attachments = []
                st.rerun() # Rerun to update the list of attachments displayed


        st.markdown("---")
        # Personalization checkbox
        st.session_state.personalize_email = st.checkbox(
            _t("Personalize emails for each recipient (replaces {{Name}}, {{Email}})"),
            value=st.session_state.get('personalize_email', True) # Default to True
        )

        if st.button(_t("Proceed to Review & Send"), use_container_width=True, disabled=not st.session_state.contacts):
            if not st.session_state.generated_subject or not st.session_state.generated_body:
                st.error(_t("Subject and Body cannot be empty to proceed."))
            else:
                st.session_state.page = 'review_send'
                st.rerun() # Rerun to navigate

# --- Page: Review & Send ---
def page_review_send():
    st.subheader(_t("2. Review & Send"))
    render_step_indicator(2)

    st.write(_t("Review your email content and contacts before sending."))

    # Email Preview
    st.markdown("---")
    st.markdown(f"**{_t('Email Preview (First Contact)')}**")
    if st.session_state.contacts:
        first_contact = st.session_state.contacts[0]
        preview_subject = st.session_state.generated_subject.replace("{{Name}}", first_contact.get("name", "")).replace("{{Email}}", first_contact.get("email", ""))
        preview_body = st.session_state.generated_body.replace("{{Name}}", first_contact.get("name", "")).replace("{{Email}}", first_contact.get("email", ""))
        
        st.write(f"**{_t('Subject')}:** {preview_subject}")
        st.markdown(f"**{_t('Body')}:**")
        st.markdown(preview_body) # Use markdown for body to render potential rich text/newlines
    else:
        st.info(_t("No contacts loaded to show a preview."))
    
    # Attached files preview
    if st.session_state.uploaded_attachments:
        st.markdown("---")
        st.markdown(f"**{_t('Attached Files')}:**")
        for att_file in st.session_state.uploaded_attachments:
            st.write(att_file.name)
    
    # Contacts Summary
    st.markdown("---")
    st.markdown(f"**{_t('Contacts Overview')}:**")
    st.write(_t("{count} valid contacts loaded.").format(count=len(st.session_state.contacts)))
    
    # Action Buttons
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        if st.button(_t("Back to Edit Email"), use_container_width=True):
            st.session_state.page = 'generate'
            st.rerun()
    with col2:
        if st.button(_t("Send All Emails"), use_container_width=True, disabled=not st.session_state.contacts):
            send_all_emails()

# --- Page: Results ---
def page_results():
    st.subheader(_t("3. Results"))
    render_step_indicator(3)

    if st.button(_t("Start New Email Session"), use_container_width=True):
        clear_session_state() # This will also set the page to 'generate' and rerun

    total_contacts = st.session_state.sending_summary.get('total_contacts', 0)
    successful_sends = st.session_state.sending_summary.get('successful', 0)
    failed_sends = st.session_state.sending_summary.get('failed', 0)

    if total_contacts > 0 and failed_sends == 0:
        st.success(_t("All emails sent successfully!"))
        st.write(_t("All {count} emails were sent without any issues.").format(count=total_contacts))
    elif total_contacts > 0 and failed_sends > 0:
        st.warning(_t("Sending complete with errors."))
        st.write(_t("Some emails failed to send. Please check the log below for details."))
    elif total_contacts == 0:
        st.info(_t("No emails were sent. Please upload contacts and generate an email first."))

    st.markdown("---")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(_t("Total Contacts"), total_contacts)
    with col2:
        st.metric(_t("Emails Successfully Sent"), successful_sends)
    with col3:
        st.metric(_t("Emails Failed to Send"), failed_sends)

    if st.session_state.email_sending_status:
        st.markdown("---")
        with st.expander(_t("Show Activity Log and Errors")):
            log_container = st.container(height=300)
            for log_entry in st.session_state.email_sending_status:
                if "ERROR" in log_entry:
                    log_container.error(log_entry)
                elif "SUCCESS" in log_entry:
                    log_container.success(log_entry)
                else:
                    log_container.info(log_entry)
            # Add download link for failed emails log
            if os.path.exists(FAILED_EMAILS_LOG_PATH) and os.path.getsize(FAILED_EMAILS_LOG_PATH) > 0:
                with open(FAILED_EMAILS_LOG_PATH, "rb") as f:
                    st.download_button(
                        label=_t("Download Failed Emails Log"),
                        data=f,
                        file_name="failed_emails.log",
                        mime="text/plain"
                    )

# --- Main App Logic ---

# Sidebar: Language Selection
with st.sidebar:
    st.header(_t("Settings"))
    chosen = st.selectbox(
        _t("Select your language"),
        options=list(LANGUAGES.keys()),
        format_func=lambda x: LANGUAGES[x], # Display full language name
        index=list(LANGUAGES.keys()).index(st.session_state.language)
    )
    if chosen != st.session_state.language:
        st.session_state.language = chosen
        set_language(st.session_state.language)
        st.rerun()

    st.markdown("---")
    st.markdown(_t("Welcome to the AI Email Assistant!"))
    st.markdown(_t("This tool helps you generate and send personalized emails efficiently."))
    st.markdown("---")

# Page Navigation
if st.session_state.page == 'generate':
    page_generate()
elif st.session_state.page == 'review_send':
    page_review_send()
elif st.session_state.page == 'results':
    page_results()