# streamlit_app.py

import streamlit as st
import pandas as pd
from data_handler import load_contacts_from_excel
from email_agent import SmartEmailAgent
from email_tool import send_email_message
from config import SENDER_EMAIL, OPENAI_API_KEY, FAILED_EMAILS_LOG_PATH, BREVO_API_KEY
from translations import LANGUAGES, _t, set_language
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
        st.session_state.attachments = [] # Stores UploadedFile objects
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
    steps = [
        {"label": _t("Generation & Setup"), "number": 1},
        {"label": _t("Preview & Send"), "number": 2},
        {"label": _t("Results"), "number": 3},
    ]
    step_html = "<div style='display: flex; justify-content: center; align-items: flex-start; gap: 60px; margin-bottom: 2rem;'>"
    for idx, step in enumerate(steps, start=1):
        if idx < current_step:
            # Completed step: green circle with checkmark
            circle = f"<div style='background: #22c55e; color: white; border-radius: 50%; width: 38px; height: 38px; display: flex; align-items: center; justify-content: center; font-size: 1.3rem; font-weight: bold; box-shadow: 0 2px 8px rgba(0,0,0,0.07); border: 2px solid #22c55e;'>✓</div>"
            label_color = "#22c55e"
        elif idx == current_step:
            # Current step: blue circle with number
            circle = f"<div style='background: #2563eb; color: white; border-radius: 50%; width: 38px; height: 38px; display: flex; align-items: center; justify-content: center; font-size: 1.3rem; font-weight: bold; box-shadow: 0 2px 8px rgba(0,0,0,0.07); border: 2px solid #2563eb;'>{step['number']}</div>"
            label_color = "#2563eb"
        else:
            # Upcoming step: gray circle with number
            circle = f"<div style='background: #e5e7eb; color: #9ca3af; border-radius: 50%; width: 38px; height: 38px; display: flex; align-items: center; justify-content: center; font-size: 1.3rem; font-weight: bold; box-shadow: 0 2px 8px rgba(0,0,0,0.04); border: 2px solid #e5e7eb;'>{step['number']}</div>"
            label_color = "#9ca3af"
        step_html += f"<div style='display: flex; flex-direction: column; align-items: center; min-width: 90px;'>"
        step_html += circle
        step_html += f"<div style='margin-top: 0.5rem; font-size: 1rem; color: {label_color}; text-align: center; font-weight: {'bold' if idx == current_step else 'normal'};'>{step['label']}</div>"
        step_html += "</div>"
    step_html += "</div>"
    st.markdown(step_html, unsafe_allow_html=True)

# --- Helper function for adding greeting ---
def _add_greeting_to_body(body_content, greeting_text, current_language):
    """
    Prepends a translated greeting to the body content, avoiding duplicates.
    """
    if not greeting_text:
        return body_content # No greeting to add

    # Get the appropriate salutation prefix based on language
    salutation_prefix = _t("Dear") # Default to "Dear"
    if current_language == 'fr':
        salutation_prefix = _t("Bonjour") # Use "Bonjour" for French

    # Check if the greeting_text already starts with a salutation in the current language
    salutations_to_check = {
        'en': ['dear', 'hello', 'hi'],
        'fr': ['cher', 'chère', 'chers', 'chères', 'bonjour', 'salut']
    }
    
    greeting_already_has_salutation = False
    for salutation_word in salutations_to_check.get(current_language, []):
        if greeting_text.lower().startswith(salutation_word):
            greeting_already_has_salutation = True
            break

    if not greeting_already_has_salutation:
        body_prefix = f"{salutation_prefix} {greeting_text},\n\n"
    else:
        body_prefix = f"{greeting_text},\n\n" # Use the greeting as is if it already contains a salutation
    
    return body_prefix + body_content

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

    # Apply greeting to editable_body only if not personalizing
    if not st.session_state.personalize_emails:
        actual_greeting = st.session_state.generic_greeting if st.session_state.generic_greeting else _t("Valued Customer")
        st.session_state.editable_body = _add_greeting_to_body(
            st.session_state.editable_body,
            actual_greeting,
            st.session_state.language
        )
        st.session_state.template_body = st.session_state.editable_body # Keep template_body updated too
        
    st.session_state.generation_in_progress = False
    st.session_state.email_generated = True # Set flag to show generated email fields
    st.session_state.page = 'preview' # Set page to preview after generation
    st.rerun() # Rerun to display the generated email

def send_all_emails():
    st.session_state.sending_in_progress = True
    status = []
    success = fail = 0
    total_contacts = len(st.session_state.contacts)

    # Initialize a progress bar
    progress_text = _t("Sending emails. Please wait.")
    my_bar = st.progress(0, text=progress_text)

    temp_attachment_paths = [] # To store paths of temporary attachment files

    # Create a temporary directory for attachments
    with tempfile.TemporaryDirectory() as temp_dir:
        try:
            # Save uploaded attachments to temporary files
            for uploaded_file in st.session_state.attachments:
                temp_file_path = os.path.join(temp_dir, uploaded_file.name)
                with open(temp_file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                temp_attachment_paths.append(temp_file_path)

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
                
                subj = st.session_state.editable_subject
                body = st.session_state.editable_body # Body already contains generic greeting if generic

                # Apply personalization to subject and body if needed
                if st.session_state.personalize_emails:
                    actual_greeting = contact.get('name', '')
                    contact_email = contact.get('email', '')

                    # Replace placeholders for Name/Nom
                    for placeholder in ["{{Name}}", "{{Nom}}"]:
                        subj = subj.replace(placeholder, actual_greeting)
                        body = body.replace(placeholder, actual_greeting)

                    # Replace placeholders for Email/Courriel
                    for placeholder in ["{{Email}}", "{{Courriel}}"]:
                        subj = subj.replace(placeholder, contact_email)
                        body = body.replace(placeholder, contact_email)
                else:
                    # For generic emails, ensure subject does not contain {{Name}} or {{Email}}
                    # These should already be handled if the AI agent inserts them, but this is a safeguard.
                    subj = subj.replace("{{Name}}", "").replace("{{Email}}", "").replace("{{Nom}}", "").replace("{{Courriel}}", "")
                    body = body.replace("{{Name}}", "").replace("{{Email}}", "").replace("{{Nom}}", "").replace("{{Courriel}}", "")


                sender_info = SENDER_EMAIL

                # Attempt to send email
                try:
                    result = send_email_message(
                        sender_email=SENDER_EMAIL,
                        sender_name=SENDER_EMAIL.split('@')[0].replace('.', ' ').title(),
                        to_email=email,
                        to_name=contact.get('name', ''),
                        subject=subj,
                        body=body,
                        attachments=temp_attachment_paths
                    )
                    if result.get('status') == 'success':
                        msg = f"Success: {contact.get('name', email)} <{email}>" # Use contact name or email for log
                        success += 1
                    else:
                        msg = f"Error: {contact.get('name', email)} <{email}> - {result.get('message')}"
                        fail += 1
                    status.append(msg)
                except Exception as e:
                    msg = f"Error: {contact.get('name', email)} <{email}> - {str(e)}"
                    status.append(msg)
                    fail += 1
        finally:
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
    if not SENDER_EMAIL or not BREVO_API_KEY:
        st.warning(_t("Sender email credentials are not configured. Please set SENDER_EMAIL and SENDER_PASSWORD in Streamlit secrets."))
    st.markdown("---")

    # --- File Upload ---
    uploaded_file = st.file_uploader(
        _t("Upload Excel (.xlsx/.xls)"),
        type=["xlsx","xls"]
    )

    # Process file only if a new file is uploaded (by name or initial upload)
    if uploaded_file is not None and \
       (st.session_state.uploaded_file_name is None or \
        st.session_state.uploaded_file_name != uploaded_file.name):
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp_file:
            shutil.copyfileobj(uploaded_file, tmp_file)
            st.session_state.uploaded_file_path = tmp_file.name # Store path for access
        
        st.session_state.uploaded_file_name = uploaded_file.name
        contacts, issues = load_contacts_from_excel(st.session_state.uploaded_file_path)
        st.session_state.contacts = contacts
        st.session_state.contact_issues = issues
        st.session_state.show_generation_section = True # Show the AI generation form
        
        if issues:
            st.warning(_t("WARNING: Some contacts had issues (e.g., missing/invalid/duplicate emails). They will be skipped."))
            for issue in issues:
                st.info(f"  - {issue}")
        
        if contacts:
            st.success(_t("Successfully loaded {count} valid contacts.", count=len(contacts)))
        else:
            st.error(_t("No valid contacts found in the Excel file."))
            st.session_state.show_generation_section = False # Hide generation if no contacts

    # Moved this block to only show if no file has been successfully uploaded yet,
    # preventing duplicate messages.
    if not st.session_state.uploaded_file_name and not st.session_state.contacts:
        st.info(_t("Please upload an Excel file to get started."))

    if st.session_state.show_generation_section:
        st.markdown("---")

        st.markdown(f"**{_t('AI Instruction: Describe the email you want to generate.')}**")
        st.session_state.user_prompt = st.text_area(
            _t("e.g., 'Draft a newsletter about our new product features.'"),
            value=st.session_state.user_prompt,
            height=100,
            key="user_prompt_input"
        )

        st.markdown(f"**{_t('Email Context (optional): Add style, tone, or specific details.')}**")
        st.session_state.user_email_context = st.text_area(
            _t("e.g., 'Friendly tone, include a call to action to visit our website.'"),
            value=st.session_state.user_email_context,
            height=80,
            key="user_email_context_input"
        )

        st.session_state.personalize_emails = st.checkbox(
            _t("Personalize emails?"),
            value=st.session_state.personalize_emails,
            key="personalize_emails_checkbox"
        )
        
        if not st.session_state.personalize_emails:
            st.session_state.generic_greeting = st.text_input(
                _t("Generic Greeting (e.g., 'Dear Valued Customer')"),
                value=st.session_state.generic_greeting,
                placeholder=_t("Enter a generic greeting if not personalizing"),
                key="generic_greeting_input"
            )

        st.markdown("---")
        if st.button(
            _t("Generate Email"),
            use_container_width=True,
            key="generate_email_button",
            disabled=st.session_state.generation_in_progress,
            type="primary"
        ):
            if st.session_state.user_prompt:
                generate_email_preview_and_template()
            else:
                st.warning(_t("Please provide instructions for the AI to generate the email."))


# --- Page: Preview ---
def page_preview():
    st.subheader(_t("2. Preview & Attachments"))
    render_step_indicator(2)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f"**{_t('Editable Email Content')}**")
        st.info(_t("Edit the email template here. Changes will reflect in the live preview."))
        st.session_state.editable_subject = st.text_input(
            _t("Subject"),
            value=st.session_state.editable_subject,
            key="preview_subject_input"
        )
        st.session_state.editable_body = st.text_area(
            _t("Body"),
            value=st.session_state.editable_body,
            height=400,
            key="preview_body_input"
        )
        st.markdown("---")
        # Button to go back to generation
        if st.button(_t("Back to Generation"), use_container_width=True, key="back_to_generation_button", type="primary"):
            st.session_state.page = 'generate'
            st.rerun()

    with col2:
        st.markdown(f"**{_t('Live Preview for First Contact')}**")
        st.info(_t("This shows how the email will appear for the first contact. To make changes, use the 'Editable Email Content' section on the left."))
        if st.session_state.contacts:
            first_contact = st.session_state.contacts[0]
            preview_name = first_contact.get('name', '')
            preview_email = first_contact.get('email', '')

            # Apply personalization for preview
            preview_subj = st.session_state.editable_subject
            preview_body = st.session_state.editable_body # Body already contains generic greeting if applicable

            if st.session_state.personalize_emails:
                # Replace {{Name}}, {{Nom}}, {{Email}}, {{Courriel}} placeholders with actual contact data
                for placeholder in ["{{Name}}", "{{Nom}}"]:
                    preview_subj = preview_subj.replace(placeholder, preview_name)
                    preview_body = preview_body.replace(placeholder, preview_name)

                for placeholder in ["{{Email}}", "{{Courriel}}"]:
                    preview_subj = preview_subj.replace(placeholder, preview_email)
                    preview_body = preview_body.replace(placeholder, preview_email)
            else:
                # For generic emails, ensure subject and body do not contain any personalization placeholders
                preview_subj = preview_subj.replace("{{Name}}", "").replace("{{Email}}", "").replace("{{Nom}}", "").replace("{{Courriel}}", "")
                preview_body = preview_body.replace("{{Name}}", "").replace("{{Email}}", "").replace("{{Nom}}", "").replace("{{Courriel}}", "")

            st.text_input(_t("Recipient"), value=f"{preview_name} <{preview_email}>") # Removed disabled=True
            st.text_input(_t("Subject"), value=preview_subj) # Removed disabled=True
            # Display the body using st.text_area, removed disabled=True
            st.text_area(_t("Body"), value=preview_body, height=350) 
        else:
            st.info(_t("Upload contacts in the first step to see a preview."))

        st.markdown("---")
        st.markdown(f"**{_t('Add Attachments')}**")
        uploaded_attachments = st.file_uploader(
            _t("Upload files"),
            type=None, # Allow all file types
            accept_multiple_files=True,
            key="attachment_uploader"
        )
        if uploaded_attachments:
            # Clear previous attachments if new ones are uploaded
            # st.session_state.attachments = [] # Decide if you want to replace or append
            for uploaded_file in uploaded_attachments:
                # Check if file is already in attachments to avoid duplicates by name
                if not any(att.name == uploaded_file.name for att in st.session_state.attachments):
                    st.session_state.attachments.append(uploaded_file)
            st.info(_t("Attachments selected: {count}", count=len(st.session_state.attachments)))
        
        if st.session_state.attachments:
            st.markdown(f"**{_t('Current Attachments')}**")
            for i, att in enumerate(st.session_state.attachments):
                col_att_name, col_att_remove = st.columns([0.8, 0.2])
                with col_att_name:
                    st.write(f"- {att.name}")
                with col_att_remove:
                    if st.button("X", key=f"remove_attachment_{i}"):
                        st.session_state.attachments.pop(i)
                        st.rerun() # Rerun to update the list


    st.markdown("---")
    if st.button(_t("Confirm Send"), use_container_width=True, key="confirm_send_button", disabled=st.session_state.sending_in_progress, type="primary"):
        if not st.session_state.contacts:
            st.warning(_t("No contacts loaded to send emails to."))
        elif not st.session_state.editable_subject or not st.session_state.editable_body:
            st.warning(_t("Subject and Body cannot be empty. Please go back to Generation if needed."))
        else:
            send_all_emails() # This will transition to the results page

# --- Page: Results ---
def page_results():
    st.subheader(_t("3. Sending Results"))
    render_step_indicator(3)

    summary = st.session_state.sending_summary
    total = summary['total_contacts']
    successful = summary['successful']
    failed = summary['failed']

    st.markdown("---")
    if total > 0 and successful == total:
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
        st.metric(_t("Total Contacts Processed"), total)
    with col2:
        st.metric(_t("Emails Sent Successfully"), successful)
    with col3:
        st.metric(_t("Emails Failed to Send"), failed)
    
    st.markdown("---")
    if st.button(_t("Show Activity Log and Errors"), use_container_width=True, key="show_log_button"):
        st.subheader(_t("Activity Log"))
        # Using a container to display log entries dynamically
        log_display_container = st.container() 
        if st.session_state.email_sending_status:
            for log_entry in st.session_state.email_sending_status:
                if "error" in log_entry.lower() or "failed" in log_entry.lower():
                    log_display_container.error(log_entry)
                elif "success" in log_entry.lower():
                    log_display_container.success(log_entry)
                else:
                    log_display_container.info(log_entry)

    st.markdown("---")
    if st.button(_t("Start New Email Session"), use_container_width=True, key="start_new_session_button", type="primary"):
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
elif st.session_state.page == 'results':
    page_results()