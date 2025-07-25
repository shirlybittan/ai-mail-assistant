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
from contextlib import contextmanager

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
</style>
""", unsafe_allow_html=True)

# --- Page Config ---
st.set_page_config(layout="wide", page_title=_t("AI Email Assistant"))

# --- Session State Initialization ---
def init_state():
    if 'initialized' not in st.session_state:
        st.session_state.language = 'fr' # Default to French as requested
        st.session_state.page = 'generate'
        st.session_state.contacts = []
        st.session_state.contact_issues = []
        st.session_state.attachments = []
        st.session_state.uploaded_attachments = []
        st.session_state.email_template = {"subject": "", "body": ""}
        st.session_state.email_preview_content = ""
        st.session_state.email_sending_status = [] # To store log messages
        st.session_state.sending_summary = {'total_contacts': 0, 'successful': 0, 'failed': 0}
        st.session_state.personalize_emails = False
        st.session_state.generic_greeting = ""
        st.session_state.sender_email_input = SENDER_EMAIL
        st.session_state.initialized = True # Mark as initialized

# Initialize state on first run
init_state()

# Set language based on session state
set_language(st.session_state.language)

# --- Email Agent Initialization ---
# This needs to be outside functions if it's used across multiple parts of the app
# and depends on a session state variable (OPENAI_API_KEY)
try:
    ai_agent = SmartEmailAgent(openai_api_key=OPENAI_API_KEY)
except ValueError as e:
    st.error(f"Configuration Error: {e}. Please ensure OPENAI_API_KEY is set in your secrets.")
    ai_agent = None # Set to None if initialization fails


# --- Utility Functions ---

def log_activity(message, level="info"):
    """Logs activity messages to session state for display."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] {message}"
    st.session_state.email_sending_status.append(log_entry)

def navigate_to(page_name):
    st.session_state.page = page_name
    st.rerun()

@contextmanager
def st_spinner_text(text):
    """Custom spinner context manager to display text during operation."""
    with st.spinner(text):
        yield

def process_uploaded_file(uploaded_file):
    """Handles the uploaded Excel file for contacts."""
    if uploaded_file is not None:
        file_extension = uploaded_file.name.split('.')[-1]
        if file_extension in ["xlsx", "xls"]:
            # Save uploaded file to a temporary location
            with tempfile.NamedTemporaryFile(delete=False, suffix=f".{file_extension}") as tmp_file:
                shutil.copyfileobj(uploaded_file, tmp_file)
                tmp_file_path = tmp_file.name

            contacts, issues = load_contacts_from_excel(tmp_file_path)
            os.remove(tmp_file_path) # Clean up the temporary file

            st.session_state.contacts = contacts
            st.session_state.contact_issues = issues

            if contacts:
                st.success(_t("Successfully loaded {count} valid contacts.", count=len(contacts)))
            if issues:
                for issue in issues:
                    st.warning(issue)
        else:
            st.error(_t("Error loading contacts: {error_message}", error_message="Unsupported file type. Please upload an .xlsx or .xls file."))
    else:
        st.session_state.contacts = []
        st.session_state.contact_issues = []

def generate_email():
    """Generates the email template using the AI agent."""
    prompt = st.session_state.prompt_input
    if not prompt:
        st.error(_t("Please enter a prompt for email generation."))
        return

    user_email_context = st.session_state.email_context if 'email_context' in st.session_state else ""

    if ai_agent:
        with st_spinner_text(_t("Generating email...")):
            generated_email = ai_agent.generate_email_template(
                prompt=prompt,
                user_email_context=user_email_context,
                output_language=st.session_state.language
            )
            if generated_email and generated_email["subject"] != "Error":
                st.session_state.email_template = generated_email
                st.success(_t("Your email has been generated! You can edit it below."))
                # Move to preview page after generation
                navigate_to('preview')
            else:
                st.error(_t("Error generating email. Please try again."))
    else:
        st.error(_t("AI Email Agent is not initialized. Check API key configuration."))


def generate_email_preview():
    """Generates a preview of the email for the first contact."""
    st.session_state.email_preview_content = "" # Clear previous preview
    if not st.session_state.contacts:
        st.warning(_t("No contacts loaded yet. Please go back to Email Generation to upload a file."))
        return

    if not st.session_state.email_template["subject"] and not st.session_state.email_template["body"]:
        st.warning(_t("No email template generated yet. Please generate an email first."))
        return

    first_contact = st.session_state.contacts[0]
    log_activity(_t("Generating email preview for the first contact. This may take a moment..."))
    log_activity(_t("Using first contact for preview: {name} ({email})", name=first_contact['name'], email=first_contact['email']))

    subject_template = st.session_state.email_template["subject"]
    body_template = st.session_state.email_template["body"]

    # Apply generic greeting if personalization is on but no specific name placeholder in template
    if st.session_state.personalize_emails and st.session_state.generic_greeting and "{{Name}}" not in body_template:
        body_template = st.session_state.generic_greeting + "\n\n" + body_template

    # Replace placeholders for preview
    preview_subject = subject_template.replace("{{Name}}", first_contact.get("name", "")).replace("{{Email}}", first_contact.get("email", ""))
    preview_body = body_template.replace("{{Name}}", first_contact.get("name", "")).replace("{{Email}}", first_contact.get("email", ""))

    st.session_state.email_preview_content = f"**{_t('Subject')}:** {preview_subject}\n\n{preview_body}"
    log_activity(_t("Email preview generated successfully."))
    st.rerun() # Rerun to display the preview immediately

def send_all_emails():
    """Sends personalized emails to all loaded contacts."""
    if not st.session_state.contacts:
        st.error(_t("No contacts to send emails to. Please upload an Excel file first."))
        return
    if not st.session_state.email_template["subject"] or not st.session_state.email_template["body"]:
        st.error(_t("Email subject or body is empty. Please generate or edit the email content."))
        return

    st.session_state.email_sending_status = [] # Clear previous log
    st.session_state.sending_summary = {'total_contacts': len(st.session_state.contacts), 'successful': 0, 'failed': 0}

    log_activity(_t("Email sending process initiated..."))
    
    # Store current values of template and personalization settings
    subject_template = st.session_state.email_template["subject"]
    body_template = st.session_state.email_template["body"]
    personalize = st.session_state.personalize_emails
    generic_greeting = st.session_state.generic_greeting
    
    sender_email_to_use = SENDER_EMAIL
    sender_password_to_use = SENDER_PASSWORD
    
    if not sender_email_to_use or not sender_password_to_use:
        st.error(_t("Sender email or password not configured. Cannot send emails."))
        log_activity(_t("Sender email or password not configured. Cannot send emails."), level="error")
        return

    # Create a simple progress bar
    progress_text = _t("Sending emails. Please wait...")
    send_progress_bar = st.progress(0, text=progress_text)
    
    for i, contact in enumerate(st.session_state.contacts):
        contact_name = contact.get("name", "Contact")
        contact_email = contact.get("email", "")

        if not contact_email:
            log_activity(_t("    - Email: error - Skipping contact {name} due to missing email.", name=contact_name), level="error")
            st.session_state.sending_summary['failed'] += 1
            continue

        log_activity(_t("--- [{current}/{total}] Processing contact: {name} ({email}) ---",
                        current=i + 1, total=len(st.session_state.contacts), name=contact_name, email=contact_email))

        personalized_subject = subject_template
        personalized_body = body_template

        # Personalize if enabled
        if personalize:
            log_activity(_t("  Generating personalized email for {name}...", name=contact_name))
            # Replace {{Name}} and {{Email}} placeholders
            personalized_subject = personalized_subject.replace("{{Name}}", contact_name).replace("{{Email}}", contact_email)
            personalized_body = personalized_body.replace("{{Name}}", contact_name).replace("{{Email}}", contact_email)
            
            # Prepend generic greeting if it exists and {{Name}} wasn't in template
            if generic_greeting and "{{Name}}" not in body_template:
                personalized_body = generic_greeting.replace("{{Name}}", contact_name).replace("{{Email}}", contact_email) + "\n\n" + personalized_body


        log_activity(_t("  Attempting Email for {name}...", name=contact_name))
        try:
            result = send_email_message(
                sender_email=sender_email_to_use,
                sender_password=sender_password_to_use,
                to_email=contact_email,
                subject=personalized_subject,
                body=personalized_body,
                attachments=[], # Attachments are not yet supported in this flow
                log_path=FAILED_EMAILS_LOG_PATH
            )

            if result['status'] == 'success':
                st.session_state.sending_summary['successful'] += 1
                log_activity(_t("    - Email: success - Email sent to {email} successfully.", email=contact_email))
            else:
                st.session_state.sending_summary['failed'] += 1
                log_activity(_t("    - Email: error - Failed to send to {email}. Details: {message}",
                                email=contact_email, message=result['message']), level="error")
        except Exception as e:
            st.session_state.sending_summary['failed'] += 1
            log_activity(_t("    - Email: error - An unexpected error occurred for {email}: {error}",
                            email=contact_email, error=str(e)), level="error")
        
        # Update progress bar
        progress_value = (i + 1) / len(st.session_state.contacts)
        send_progress_bar.progress(progress_value, text=progress_text)

    log_activity(_t("--- Email sending process complete ---"))
    log_activity(_t("Summary: {successful} successful, {failed} failed/skipped.",
                    successful=st.session_state.sending_summary['successful'],
                    failed=st.session_state.sending_summary['failed']))
    send_progress_bar.empty() # Remove progress bar after completion
    
    navigate_to('results') # Move to results page after sending

# --- Page: Email Generation ---
def page_generate():
    st.subheader(_t("1. Email Generation"))
    render_step_indicator(1)

    # Email generation prompt from AI
    st.text_area(
        _t("Compose your email details below."),
        key="prompt_input",
        height=150,
        placeholder=_t("e.g., 'Write a welcome email for new users, offering a 10% discount on their first purchase.'")
    )

    # AI Generation button
    col_ai_gen, col_clear = st.columns(2)
    with col_ai_gen:
        if st.button(_t("Generate Email"), use_container_width=True):
            generate_email()
    with col_clear:
        if st.button(_t("Clear Form"), use_container_width=True):
            st.session_state.prompt_input = ""
            st.session_state.email_template = {"subject": "", "body": ""}
            st.session_state.email_preview_content = ""
            st.session_state.contacts = []
            st.session_state.contact_issues = []
            st.session_state.email_sending_status = []
            st.session_state.sending_summary = {'total_contacts': 0, 'successful': 0, 'failed': 0}
            st.session_state.personalize_emails = False
            st.session_state.generic_greeting = ""
            st.rerun()
            
    st.markdown("---")
    
    st.write(_t("Your email has been generated! You can edit it below."))

    # Display and allow editing of generated email
    st.text_input(_t("Subject"), value=st.session_state.email_template["subject"], key="edited_subject")
    st.text_area(_t("Body"), value=st.session_state.email_template["body"], height=300, key="edited_body")

    # Update session state with edited content
    st.session_state.email_template["subject"] = st.session_state.edited_subject
    st.session_state.email_template["body"] = st.session_state.edited_body
    
    st.text_input(_t("Sender"), value=st.session_state.sender_email_input, key="sender_email_input_field",
                  help=_t("This will be the 'From' address in the email."))

    st.session_state.sender_email_input = st.session_state.sender_email_input_field


    st.markdown("---")

    st.markdown(f"**{_t('Upload an Excel file with contacts (.xlsx)')}**")
    uploaded_file = st.file_uploader(
        _t("Drag and drop file here"),
        type=["xlsx", "xls"],
        accept_multiple_files=False,
        key="contact_file_uploader",
        help="Limit 200MB per file • XLSX, XLS"
    )

    # Process uploaded file immediately if it changes
    if uploaded_file is not None and uploaded_file != st.session_state.get('last_uploaded_file'):
        process_uploaded_file(uploaded_file)
        st.session_state['last_uploaded_file'] = uploaded_file # Store the current file to prevent re-processing
    elif uploaded_file is None and st.session_state.get('last_uploaded_file') is not None:
        # If file was removed, clear contacts
        st.session_state.contacts = []
        st.session_state.contact_issues = []
        st.session_state['last_uploaded_file'] = None
        st.rerun() # Rerun to clear the displayed contacts
    
    # Display loaded contacts count if available
    if st.session_state.contacts:
        st.info(_t("Successfully loaded {count} valid contacts.", count=len(st.session_state.contacts)))
        
    st.markdown("---")

    if st.button(_t("2. Email Preview & Send"), use_container_width=True):
        navigate_to('preview')

# --- Page: Email Preview & Send ---
def page_preview():
    st.subheader(_t("2. Email Preview & Send"))
    render_step_indicator(2)

    if not st.session_state.contacts:
        st.warning(_t("No contacts loaded yet. Please go back to Email Generation to upload a file."))
        if st.button(_t("Back to Email Generation")):
            navigate_to('generate')
        return

    # Personalization checkbox
    st.checkbox(
        _t("Customize emails for each recipient (replaces {{Name}}, {{Email}})"),
        key="personalize_emails",
        value=st.session_state.personalize_emails
    )

    if st.session_state.personalize_emails:
        st.text_input(
            _t("Generic Greeting Placeholder (e.g., 'Dear {{Name}}' or 'Hello')"),
            key="generic_greeting",
            value=st.session_state.generic_greeting,
            placeholder=_t("e.g., 'Dear {{Name}}' or 'Hello'")
        )

    st.markdown("---")

    # Email Preview
    st.markdown(f"### {_t('Email Preview')}")
    if st.button(_t("Generate Email Preview")):
        generate_email_preview()

    if st.session_state.email_preview_content:
        st.markdown(st.session_state.email_preview_content)
    else:
        st.info(_t("No email preview available. Generate an email and load contacts first."))

    st.markdown("---")
    
    st.write(f"**{_t('Total Contacts to Send')}:** {len(st.session_state.contacts)}")

    col_back, col_send = st.columns(2)
    with col_back:
        if st.button(_t("Back to Email Generation"), use_container_width=True):
            navigate_to('generate')
    with col_send:
        if st.button(_t("Confirm Send"), use_container_width=True):
            send_all_emails()

# --- Page: Results ---
def page_results():
    st.subheader(_t("3. Results"))
    render_step_indicator(3)
    if st.button(_t("Start New Email Session"), use_container_width=True):
        # Clear all relevant session states for a new session
        for k in list(st.session_state.keys()):
            if k not in ['language', 'initialized']: # Keep language and initialized state
                del st.session_state[k]
        init_state() # Re-initialize defaults
        st.rerun()
        
    total = st.session_state.sending_summary.get('total_contacts', 0)
    suc = st.session_state.sending_summary.get('successful', 0)
    fail = st.session_state.sending_summary.get('failed', 0)

    st.markdown("---")

    if fail == 0 and suc > 0:
        st.success(_t("All emails sent successfully!"))
        st.write(_t("All {count} emails were sent without any issues.", count=total))
    else:
        st.warning(_t("Sending complete with errors."))
        st.write(_t("Some emails failed to send. Please check the log below for details."))
        
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

# --- Step Indicator ---
def render_step_indicator(current_step):
    steps = {
        1: _t("1. Email Generation"),
        2: _t("2. Email Preview & Send"),
        3: _t("3. Results")
    }
    
    cols = st.columns(len(steps))
    for i, (step_num, step_name) in enumerate(steps.items()):
        if step_num == current_step:
            cols[i].markdown(f"**<span style='color: #4CAF50;'>{step_name} &raquo;</span>**", unsafe_allow_html=True)
        else:
            cols[i].markdown(f"<span style='color: grey;'>{step_name}</span>", unsafe_allow_html=True)
    st.markdown("---")

# --- Main Application Logic ---
st.title(_t("AI Email Assistant"))

st.write(_t("Welcome! Use the sidebar to navigate."))


# --- Sidebar: Language Selection ---
with st.sidebar:
    chosen = st.selectbox(
        _t("Language"), options=list(LANGUAGES.keys()),
        index=list(LANGUAGES.keys()).index(st.session_state.language),
        format_func=lambda x: LANGUAGES[x] # Display full language name
    )
    if chosen != st.session_state.language:
        st.session_state.language = chosen
        set_language(chosen)
        st.rerun() # Rerun app to apply language change

    st.markdown("---")
    st.markdown("### Navigation")
    if st.button(_t("1. Email Generation"), key="nav_generate", use_container_width=True):
        navigate_to('generate')
    if st.button(_t("2. Email Preview & Send"), key="nav_preview", use_container_width=True,
                 disabled=not st.session_state.email_template["subject"] or not st.session_state.contacts):
        # Disable if no email generated or no contacts loaded
        navigate_to('preview')
    if st.button(_t("3. Results"), key="nav_results", use_container_width=True,
                 disabled=st.session_state.sending_summary['total_contacts'] == 0):
        # Disable if no emails have been attempted to send
        navigate_to('results')


# --- Render Current Page ---
if st.session_state.page == 'generate':
    page_generate()
elif st.session_state.page == 'preview':
    page_preview()
elif st.session_state.page == 'results':
    page_results()