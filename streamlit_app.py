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
        st.session_state.initialized = True
        # New state variable for tracking the last uploaded file ID
        st.session_state.last_uploaded_file_id = None 
init_state()

# --- UI Helpers ---
def render_step_indicator(current_step: int):
    steps = [_t("1. Generation"), _t("2. Preview"), _t("3. Results")]
    cols = st.columns(len(steps))
    for idx, label in enumerate(steps, start=1):
        text = f"▶ {label}" if idx == current_step else label
        with cols[idx-1]:
            st.markdown(f"**{text}**")

@contextmanager
def card_container():
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    yield
    st.markdown("</div>", unsafe_allow_html=True)

# --- Business Logic ---
def generate_email_preview_and_template():
    st.session_state.generation_in_progress = True
    agent = SmartEmailAgent(openai_api_key=OPENAI_API_KEY)
    template = agent.generate_email_template(
        prompt=st.session_state.user_prompt,
        user_email_context=st.session_state.user_email_context,
        output_language=st.session_state.language
    )
    st.session_state.template_subject = template['subject']
    st.session_state.template_body = template['body']
    st.session_state.editable_subject = template['subject']
    st.session_state.editable_body = template['body']
    st.session_state.page = 'preview'
    st.session_state.generation_in_progress = False


def send_all_emails():
    st.session_state.sending_in_progress = True
    status = []
    success = fail = 0
    for contact in st.session_state.contacts:
        name = contact.get('name') or st.session_state.generic_greeting
        email = contact.get('email')
        subj = st.session_state.editable_subject.replace('{{Name}}', name).replace('{{Email}}', email)
        body = st.session_state.editable_body.replace('{{Name}}', name).replace('{{Email}}', email)
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
                msg = f"Success: {name} <{email}>"
                success += 1
            else:
                msg = f"Error: {name} <{email}> - {result.get('message')}"
                fail += 1
            status.append(msg)
        except Exception as e:
            msg = f"Error: {name} <{email}> - {str(e)}"
            status.append(msg)
            fail += 1
    st.session_state.email_sending_status = status
    st.session_state.sending_summary = {
        'total_contacts': len(st.session_state.contacts),
        'successful': success,
        'failed': fail
    }
    st.session_state.page = 'results'
    st.session_state.sending_in_progress = False

# --- Page: Generate ---
def page_generate():
    st.subheader(_t("1. Email Generation"))
    render_step_indicator(1)
    # --- File Upload ---
    if 'uploaded_file' not in st.session_state:
        st.session_state.uploaded_file = None
    if 'show_generation' not in st.session_state:
        st.session_state.show_generation = False

    uploaded_file = st.file_uploader(
        _t("Upload Excel (.xlsx/.xls)"), type=["xlsx","xls"]
    )

    current_file_id = None
    if uploaded_file is not None:
        # Get the ID of the currently uploaded file safely
        current_file_id = uploaded_file.id

    # Process file only if it's a new upload or different from the last processed one
    if current_file_id is not None and \
       (st.session_state.last_uploaded_file_id is None or \
        st.session_state.last_uploaded_file_id != current_file_id):
        
        # Only process if a new or different file has been uploaded
        contacts, issues = load_contacts_from_excel(uploaded_file)
        st.session_state.contacts = contacts
        st.session_state.contact_issues = issues
        st.session_state.uploaded_file = uploaded_file
        st.session_state.last_uploaded_file_id = current_file_id # Store the ID of the new file
        st.session_state.show_generation = False

    # --- Show results of upload ---
    if st.session_state.uploaded_file is not None:
        count = len(st.session_state.contacts) if 'contacts' in st.session_state else 0
        st.success(_t("Loaded {count} contacts.", count=count))
        for issue in st.session_state.get('contact_issues', []):
            st.warning(issue)
        # Always show Next button after upload
        if not st.session_state.show_generation:
            if st.button(_t("Next"), use_container_width=True):
                st.session_state.show_generation = True
        else:
            # --- Generation form ---
            st.session_state.personalize_emails = st.checkbox(
                _t("Personalize emails?"), value=st.session_state.personalize_emails
            )
            if not st.session_state.personalize_emails:
                st.session_state.generic_greeting = st.text_input(
                    _t("Generic Greeting"), value=st.session_state.generic_greeting
                )
            st.session_state.user_prompt = st.text_area(
                _t("AI Instruction"), value=st.session_state.user_prompt
            )
            st.session_state.user_email_context = st.text_area(
                _t("Email Context (optional)"), value=st.session_state.user_email_context
            )
            if st.button(_t("Generate Email"), use_container_width=True):
                generate_email_preview_and_template()

# --- Page: Preview ---
def page_preview():
    st.subheader(_t("2. Preview & Attachments"))
    render_step_indicator(2)
    col1, col2 = st.columns(2)
    with col1:
        with card_container():
            st.session_state.editable_subject = st.text_input(
                _t("Subject"), value=st.session_state.editable_subject
            )
            st.session_state.editable_body = st.text_area(
                _t("Body"), value=st.session_state.editable_body
            )
    with col2:
        with st.expander(_t("Live Preview"), expanded=True):
            if st.session_state.contacts:
                first = st.session_state.contacts[0]
                name = first.get('name') or st.session_state.generic_greeting
                email = first.get('email')
                preview_subj = st.session_state.editable_subject.replace("{{Name}}", name).replace("{{Email}}", email)
                preview_body = st.session_state.editable_body.replace("{{Name}}", name).replace("{{Email}}", email)
                st.markdown(f"**Subject:** {preview_subj}")
                st.markdown(preview_body.replace('\n','  \n'), unsafe_allow_html=True)
    files = st.file_uploader(
        _t("Add Attachments"), accept_multiple_files=True
    )
    if files:
        st.session_state.attachments = files
    if st.button(_t("Confirm Send"), use_container_width=True):
        send_all_emails()

# --- Page: Results ---
def page_results():
    st.subheader(_t("3. Results"))
    render_step_indicator(3)
    if st.button(_t("Start New Email Session"), use_container_width=True):
        for k in list(st.session_state.keys()):
            del st.session_state[k]
        init_state()
        
    total = st.session_state.sending_summary['total_contacts']
    suc = st.session_state.sending_summary['successful']
    fail = st.session_state.sending_summary['failed']
    c1, c2, c3 = st.columns(3)
    c1.metric(_t("Total"), total)
    c2.metric(_t("Success"), suc)
    c3.metric(_t("Failed"), fail)
    with st.expander(_t("Activity Log"), expanded=False):
        for msg in st.session_state.email_sending_status:
            if msg.startswith("Success"):
                st.success(msg)
            else:
                st.error(msg)

# --- Sidebar: Language Selection ---
with st.sidebar:
    chosen = st.selectbox(
        _t("Language"), options=list(LANGUAGES.keys()),
        index=list(LANGUAGES.keys()).index(st.session_state.language)
    )
    if chosen != st.session_state.language:
        st.session_state.language = chosen
        set_language(chosen)
        

# --- Main Navigation ---
if st.session_state.page == 'generate':
    page_generate()
elif st.session_state.page == 'preview':
    page_preview()
else:
    page_results()