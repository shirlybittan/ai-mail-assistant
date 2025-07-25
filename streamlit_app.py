# streamlit_app.py
import streamlit as st
import pandas as pd
from data_handler import load_contacts_from_excel
from email_agent import SmartEmailAgent
from email_tool import send_email_message
from config import SENDER_CREDENTIALS, OPENAI_API_KEY, SENDER_EMAIL, SENDER_PASSWORD, FAILED_EMAILS_LOG_PATH
from translations import LANGUAGES, _t, set_language
from contextlib import contextmanager
import datetime
import re
import os
import shutil

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
        st.session_state.language = 'fr'
        st.session_state.page = 'generate'
        st.session_state.contacts = []
        st.session_state.contact_issues = []
        st.session_state.attachments = []
        st.session_state.email_template = {"subject": "", "body": ""}
        st.session_state.uploaded_file = None
        st.session_state.sending_summary = {'total_contacts': 0, 'successful': 0, 'failed': 0}
        st.session_state.email_sending_status = [] # List to hold log messages for the UI
        st.session_state.personalized_preview_body = ""
        st.session_state.personalized_preview_subject = ""
        st.session_state.user_instruction = ""
        st.session_state.email_context = ""
        st.session_state.allow_personalized_salutation_override = False
        st.session_state.initialized = True

init_state() # Initialize state on first run

# --- Global Variables / Access from config (defined at top scope) ---
# Ensure these are only accessed if they exist
selected_sender_email = SENDER_EMAIL
selected_sender_password = SENDER_PASSWORD

# --- Initialize AI Agent ---
try:
    email_agent = SmartEmailAgent(openai_api_key=OPENAI_API_KEY)
except ValueError as e:
    st.error(f"Configuration Error: {e}. Please set your OpenAI API Key in Streamlit secrets.")
    email_agent = None # Set to None to prevent further errors

# --- Helper Functions ---
def _log_activity(message, level="info"):
    timestamp = datetime.datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    log_entry = f"{timestamp} {message}"
    if level == "error":
        st.session_state.email_sending_status.append(f"ERROR: {log_entry}")
    elif level == "warning":
        st.session_state.email_sending_status.append(f"WARNING: {log_entry}")
    else:
        st.session_state.email_sending_status.append(log_entry)
    # For actual logging to a file, you'd append to FAILED_EMAILS_LOG_PATH or a separate full log file.

def replace_placeholders(text, contact):
    """Replaces {{Name}} and {{Email}} placeholders in text with actual contact data."""
    # Ensure contact is not None and has the necessary keys
    if contact and "name" in contact and "email" in contact:
        text = text.replace("{{Name}}", contact["name"])
        text = text.replace("{{Email}}", contact["email"])
    return text

def render_step_indicator(current_step):
    steps = {
        1: _t("1. Email Generation"),
        2: _t("2. Preview & Send"),
        3: _t("3. Results")
    }
    cols = st.columns(len(steps))
    for i, (step_num, step_name) in enumerate(steps.items()):
        with cols[i]:
            if step_num == current_step:
                st.markdown(f"<h3 style='text-align: center; color: #1e90ff;'>▶ {step_name}</h3>", unsafe_allow_html=True)
            else:
                st.markdown(f"<h3 style='text-align: center; color: #6c757d;'>{step_name}</h3>", unsafe_allow_html=True)
    st.markdown("---")

def generate_email_preview(template_subject, template_body, contact):
    """Generates a personalized subject and body for preview."""
    personalized_subject = replace_placeholders(template_subject, contact)
    personalized_body = replace_placeholders(template_body, contact)
    return personalized_subject, personalized_body

def send_all_emails():
    st.session_state.email_sending_status = [] # Clear previous log
    st.session_state.sending_summary = {'total_contacts': len(st.session_state.contacts), 'successful': 0, 'failed': 0}

    _log_activity(_t("Email sending process initiated..."))

    if not st.session_state.contacts:
        _log_activity(_t("No contacts to send emails to."), level="warning")
        return

    # Create a temporary directory for attachments
    temp_attachments_dir = None
    attached_file_paths = []
    if st.session_state.attachments:
        temp_attachments_dir = tempfile.mkdtemp()
        for uploaded_file in st.session_state.attachments:
            file_path = os.path.join(temp_attachments_dir, uploaded_file.name)
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            attached_file_paths.append(file_path)

    for i, contact in enumerate(st.session_state.contacts):
        contact_name = contact.get("name", _t("Unknown Name"))
        contact_email = contact.get("email", _t("unknown@example.com"))

        _log_activity(_t("--- [{current}/{total}] Processing contact: {name} ({email}) ---",
                                    current=i+1, total=len(st.session_state.contacts),
                                    name=contact_name, email=contact_email))

        if not contact_email or not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', contact_email):
            _log_activity(_t("  Skipping invalid email for {name}: {email}", name=contact_name, email=contact_email), level="warning")
            st.session_state.sending_summary['failed'] += 1
            continue

        personalized_subject = replace_placeholders(st.session_state.email_template['subject'], contact)
        personalized_body = replace_placeholders(st.session_state.email_template['body'], contact)

        _log_activity(_t("  Attempting Email for {name}...", name=contact_name))

        # Pass attachments to send_email_message
        result = send_email_message(
            sender_email=selected_sender_email,
            sender_password=selected_sender_password,
            to_email=contact_email,
            subject=personalized_subject,
            body=personalized_body,
            log_path=FAILED_EMAILS_LOG_PATH,
            attachment_paths=attached_file_paths if st.session_state.attachments else []
        )

        if result and result.get("status") == "success":
            _log_activity(_t("    - Email: success - Email sent to {email} successfully.", email=contact_email), level="info")
            st.session_state.sending_summary['successful'] += 1
        else:
            error_message = result.get("message", _t("Unknown error.")) if result else _t("No result from email tool.")
            _log_activity(_t("    - Email: error - Failed to send to {email}. Details: {details}",
                                        email=contact_email, details=error_message), level="error")
            st.session_state.sending_summary['failed'] += 1

    _log_activity(_t("--- Email sending process complete ---"))
    _log_activity(_t("Summary: {successful} successful, {failed} failed/skipped.",
                                successful=st.session_state.sending_summary['successful'],
                                failed=st.session_state.sending_summary['failed']))

    # Clean up temporary attachment directory
    if temp_attachments_dir and os.path.exists(temp_attachments_dir):
        shutil.rmtree(temp_attachments_dir)

    st.session_state.page = 'results'
    st.rerun()

# --- Page: Email Generation ---
def page_generate():
    render_step_indicator(1)
    st.subheader(_t("1. Email Generation"))
    st.write(_t("Compose your email details below."))

    # User input for email generation
    st.session_state.user_instruction = st.text_area(
        _t("Describe the email you want to generate (e.g., 'A welcome email for new users, thanking them for signing up and providing a link to our tutorial.')."),
        value=st.session_state.user_instruction,
        height=100
    )
    st.session_state.email_context = st.text_area(
        _t("Additional context or style preferences for the email (e.g., 'Keep it concise and professional.')."),
        value=st.session_state.email_context,
        height=80
    )

    col1, col2 = st.columns(2)
    with col1:
        chosen_language = st.selectbox(
            _t("Output Language for AI Generation"),
            options=list(LANGUAGES.keys()),
            format_func=lambda x: LANGUAGES[x],
            index=list(LANGUAGES.keys()).index(st.session_state.language)
        )
        if chosen_language != st.session_state.language:
            st.session_state.language = chosen_language
            set_language(chosen_language)
            st.rerun()

    with col2:
        st.session_state.allow_personalized_salutation_override = st.checkbox(
            _t("Allow personalized salutation (e.g., 'Dear {{Name}}')"),
            value=st.session_state.allow_personalized_salutation_override,
            help=_t("If checked, the AI will be encouraged to use a personalized salutation. If unchecked, the AI might generate a generic one like 'Dear Customer'.")
        )

    if st.button(_t("Generate Email Content"), use_container_width=True, type="primary"):
        if email_agent:
            with st.spinner(_t("Generating email content with AI... This may take a moment.")):
                # Pass the personalization preference to the agent
                ai_generated_email = email_agent.generate_email_template(
                    prompt=st.session_state.user_instruction,
                    user_email_context=st.session_state.email_context,
                    output_language=st.session_state.language,
                    # Pass the flag to the agent
                    allow_personalized_salutation_override=st.session_state.allow_personalized_salutation_override
                )
                if ai_generated_email:
                    st.session_state.email_template['subject'] = ai_generated_email['subject']
                    st.session_state.email_template['body'] = ai_generated_email['body']
                    st.success(_t("Your email has been generated! You can modify it below."))
                else:
                    st.error(_t("Error generating email. Please try again."))
        else:
            st.error(_t("AI Email Agent not initialized. Please check configuration."))

    st.text_input(_t("Subject"), key="subject_input", value=st.session_state.email_template['subject'],
                  placeholder=_t("Enter a subject"),
                  on_change=lambda: st.session_state.email_template.__setitem__('subject', st.session_state.subject_input))
    st.text_area(_t("Body"), key="body_input", value=st.session_state.email_template['body'],
                 placeholder=_t("Enter email body"), height=300,
                 on_change=lambda: st.session_state.email_template.__setitem__('body', st.session_state.body_input))

    st.markdown("---")
    st.subheader(_t("Contact List Upload"))
    uploaded_file = st.file_uploader(
        _t("Upload an Excel file with contacts (.xlsx)"),
        type=["xlsx"],
        key="contacts_uploader"
    )

    if uploaded_file and uploaded_file != st.session_state.uploaded_file:
        st.session_state.uploaded_file = uploaded_file
        # Save the uploaded file to a temporary location
        with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp_file:
            shutil.copyfileobj(uploaded_file, tmp_file)
            temp_file_path = tmp_file.name

        contacts, issues = load_contacts_from_excel(temp_file_path)
        os.remove(temp_file_path) # Clean up the temporary file

        st.session_state.contacts = contacts
        st.session_state.contact_issues = issues
        if contacts:
            st.success(_t("Successfully loaded {count} valid contacts.", count=len(contacts)))
        if issues:
            st.warning(_t("Some contacts had issues (e.g., missing/invalid/duplicate emails). They will be skipped."))
            for issue in issues:
                st.info(f"- {issue}")

    if st.session_state.contacts:
        st.write(_t("Contacts loaded: {count}", count=len(st.session_state.contacts)))
        with st.expander(_t("View Contacts")):
            df_contacts = pd.DataFrame(st.session_state.contacts)
            st.dataframe(df_contacts, height=200)

    st.markdown("---")
    st.subheader(_t("Attachments (Optional)"))
    uploaded_attachments = st.file_uploader(
        _t("Upload files to attach to all emails"),
        type=None, # Allow all file types
        accept_multiple_files=True,
        key="attachments_uploader"
    )
    if uploaded_attachments:
        st.session_state.attachments = uploaded_attachments
        st.info(_t("Successfully uploaded {count} attachments.", count=len(st.session_state.attachments)))

        with st.expander(_t("View Attachments")):
            for attach_file in st.session_state.attachments:
                st.write(f"- {attach_file.name} ({round(attach_file.size / 1024, 2)} KB)")

    st.markdown("---")
    st.subheader(_t("Email Action"))
    col_action1, col_action2 = st.columns(2)
    with col_action1:
        if st.button(_t("Clear Form"), use_container_width=True):
            for k in list(st.session_state.keys()):
                if k not in ['language', 'initialized']: # Keep language and initialized state
                    del st.session_state[k]
            init_state() # Re-initialize relevant states
            st.rerun()
    with col_action2:
        if st.button(_t("Proceed to Preview & Send"), use_container_width=True, type="primary"):
            if not st.session_state.email_template['subject'] or not st.session_state.email_template['body']:
                st.error(_t("Subject and Body cannot be empty to proceed."))
            elif not st.session_state.contacts:
                st.error(_t("Please upload contacts to proceed."))
            else:
                st.session_state.page = 'preview_send'
                st.rerun()

# --- Page: Preview & Send ---
def page_preview_send():
    render_step_indicator(2)
    st.subheader(_t("2. Preview & Send"))

    if not st.session_state.contacts:
        st.warning(_t("No contacts loaded. Please go back to Email Generation to upload contacts."))
        if st.button(_t("Go back to Email Generation"), use_container_width=True):
            st.session_state.page = 'generate'
            st.rerun()
        return

    st.write(_t("Review your email content and send to your contacts."))

    first_contact = st.session_state.contacts[0] # Get the first contact for preview
    st.info(_t("Generating email preview for the first contact: {name} ({email}). This may take a moment...",
                            name=first_contact.get("name", "Contact"), email=first_contact.get("email", "")))

    if st.session_state.email_template['subject'] and st.session_state.email_template['body']:
        personalized_subject, personalized_body = generate_email_preview(
            st.session_state.email_template['subject'],
            st.session_state.email_template['body'],
            first_contact
        )
        st.session_state.personalized_preview_subject = personalized_subject
        st.session_state.personalized_preview_body = personalized_body
    else:
        st.warning(_t("Email template is empty. Please generate or enter content on the previous page."))
        st.session_state.personalized_preview_subject = _t("No Subject")
        st.session_state.personalized_preview_body = _t("No Body")

    st.markdown("---")
    st.subheader(_t("Editable Email Content"))

    st.text_input(_t("Subject"), value=st.session_state.email_template['subject'],
                  key="preview_subject_input",
                  on_change=lambda: st.session_state.email_template.__setitem__('subject', st.session_state.preview_subject_input))
    st.text_area(_t("Body"), value=st.session_state.email_template['body'], height=300,
                 key="preview_body_input",
                 on_change=lambda: st.session_state.email_template.__setitem__('body', st.session_state.preview_body_input))

    st.markdown("---")
    st.subheader(_t("Live Preview for First Contact"))

    st.markdown(f"**{_t('Subject')}:** {st.session_state.personalized_preview_subject}")
    st.markdown(f"**{_t('Body')}:**")
    st.markdown(st.session_state.personalized_preview_body.replace('\n', '<br>'), unsafe_allow_html=True) # Display with line breaks

    st.markdown("---")
    st.write(_t("Total contacts to send to: {count}", count=len(st.session_state.contacts)))
    if st.session_state.attachments:
        st.write(_t("Attachments: {count}", count=len(st.session_state.attachments)))
        with st.expander(_t("View Attached Files")):
            for attach_file in st.session_state.attachments:
                st.write(f"- {attach_file.name}")

    col_send1, col_send2 = st.columns(2)
    with col_send1:
        if st.button(_t("Back to Email Generation"), use_container_width=True):
            st.session_state.page = 'generate'
            st.rerun()
    with col_send2:
        if st.button(_t("Confirm Send All Emails"), use_container_width=True, type="primary"):
            send_all_emails()

# --- Page: Results ---
def page_results():
    st.subheader(_t("3. Results"))
    render_step_indicator(3)
    if st.button(_t("Start New Email Session"), use_container_width=True):
        for k in list(st.session_state.keys()):
            del st.session_state[k]
        init_state()
        st.rerun()

    total = st.session_state.sending_summary['total_contacts']
    suc = st.session_state.sending_summary['successful']
    fail = st.session_state.sending_summary['failed']

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

# --- Main App Logic ---
set_language(st.session_state.language)

# --- Sidebar: Language Selection ---
with st.sidebar:
    st.markdown(f"## {_t('Settings')}")
    chosen = st.selectbox(
        _t("Select your language"), options=list(LANGUAGES.keys()),
        index=list(LANGUAGES.keys()).index(st.session_state.language),
        format_func=lambda x: LANGUAGES[x],
        key="sidebar_language_select"
    )
    if chosen != st.session_state.language:
        st.session_state.language = chosen
        set_language(chosen)
        st.rerun()

st.title(_t("AI Email Assistant"))
st.write(_t("Welcome to the AI Email Assistant!"))

# Page navigation
if st.session_state.page == 'generate':
    page_generate()
elif st.session_state.page == 'preview_send':
    page_preview_send()
elif st.session_state.page == 'results':
    page_results()