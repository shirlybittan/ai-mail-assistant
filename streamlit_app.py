# streamlit_app.py

import streamlit as st
import pandas as pd
from data_handler import load_contacts_from_excel
from email_generator import SmartEmailAgent
from email_tool import send_email_message
# Import individual variables from config
from config import SENDER_CREDENTIALS, OPENAI_API_KEY, SENDER_EMAIL, SENDER_PASSWORD, FAILED_EMAILS_LOG_PATH
import tempfile
import os
import shutil
import datetime

# --- IMPORT LANGUAGE HELPER ---
from translations import LANGUAGES, _t # Import LANGUAGES for selectbox options, and _t for translation


# Set Streamlit page configuration
st.set_page_config(layout="wide", page_title=_t("AI Email Assistant")) # Translated title

# Initialize session state for language
if 'language' not in st.session_state:
    st.session_state.language = "fr" # <--- Langue par défaut changée en français

# Language selector - placed at the top right
col_lang_select, _ = st.columns([0.2, 0.8])
with col_lang_select:
    st.session_state.language = st.selectbox(
        label="Language", # Le libellé du selectbox lui-même est difficilement traduisible directement
        options=list(LANGUAGES.keys()),
        format_func=lambda x: LANGUAGES[x], # Cela affichera "English" ou "Français"
        key="language_selector"
    )

st.title(f"📧 {_t('AI Email Assistant')}") # Titre mis à jour avec icône et traduction

# --- DEBUGGING INFO START ---
#st.subheader(_t("Debugging Info (REMOVE AFTER TROUBLESHOOTING)")) # TRADUIT
#st.write(f"{_t('All secrets from st.secrets:')}", st.secrets.to_dict()) # TRADUIT
#st.write(f"{_t('Sender credentials (from config):')}", SENDER_CREDENTIALS) # TRADUIT
#st.write(f"{_t('OpenAI key (from config):')}", OPENAI_API_KEY) # TRADUIT
#st.write(f"{_t('DEBUG: SENDER_EMAIL retrieved:')}", SENDER_EMAIL) # TRADUIT
#st.write(f"{_t('DEBUG: SENDER_PASSWORD present:')}", bool(SENDER_PASSWORD)) # TRADUIT
#st.write(f"{_t('DEBUG: FAILED_EMAILS_LOG_PATH:')}", FAILED_EMAILS_LOG_PATH) # TRADUIT
#st.markdown("---")
# --- DEBUGGING INFO END ---


# --- Initialize session state variables ---
if 'generated_emails' not in st.session_state:
    st.session_state.generated_emails = []
if 'email_sending_status' not in st.session_state:
    st.session_state.email_sending_status = []
if 'show_preview' not in st.session_state:
    st.session_state.show_preview = False
if 'uploaded_attachments' not in st.session_state:
    st.session_state.uploaded_attachments = []
if 'contacts' not in st.session_state:
    st.session_state.contacts = []
if 'contact_issues' not in st.session_state:
    st.session_state.contact_issues = []
if 'user_prompt' not in st.session_state:
    st.session_state.user_prompt = ""
if 'user_email_context' not in st.session_state:
    st.session_state.user_email_context = ""
if 'personalize_emails' not in st.session_state:
    st.session_state.personalize_emails = False


# --- Configuration and User Input ---
st.header(_t("Configuration"))

# Check if sender credentials and OpenAI API key are loaded from config.py
if not SENDER_EMAIL or not SENDER_PASSWORD:
    st.error(_t("Sender email or password not found. Please configure them correctly in Streamlit Secrets under [app_credentials]."))
    st.stop()
if not OPENAI_API_KEY:
    st.error(_t("OpenAI API Key not found. Please configure it correctly in Streamlit Secrets under [app_credentials]."))
    st.stop()

# Display the single sender email instead of a selectbox
st.info(f"{_t('Using sender email:')} **{SENDER_EMAIL}**")
selected_sender_email = SENDER_EMAIL # Set the selected email directly


# File uploader for contacts list
uploaded_file = st.file_uploader(_t("Upload your contacts Excel file"), type=["xlsx", "xls"])

if uploaded_file is not None:
    st.session_state.contacts, st.session_state.contact_issues = load_contacts_from_excel(uploaded_file)
    if st.session_state.contacts:
        st.success(f"{_t('Loaded ')}{len(st.session_state.contacts)}{_t(' contacts.')}")
    if st.session_state.contact_issues:
        st.warning(_t("Some contacts had issues:"))
        for issue in st.session_state.contact_issues:
            st.write(f"- {issue}")
else:
    st.info(_t("Please upload an Excel file to proceed."))
    st.session_state.contacts = [] # Clear contacts if file is removed

# Add attachments
st.subheader(_t("Add Attachments (Optional)"))
st.session_state.uploaded_attachments = st.file_uploader(
    _t("Upload photos, videos, or documents (recommended total size < 25MB per mail)"),
    type=[
        "png", "jpg", "jpeg", "gif",
        "mp4", "mov", "avi",
        "pdf",
        "doc", "docx",
        "xls", "xlsx",
        "ppt", "pptx",
        "txt", "csv", "rtf"
    ],
    accept_multiple_files=True,
    key="attachment_uploader"
)

if st.session_state.uploaded_attachments:
    st.info(f"{len(st.session_state.uploaded_attachments)}{_t(' file(s) selected for attachment.')}")

# User input for email generation
st.subheader(_t("Email Content Request"))
st.session_state.user_prompt = st.text_area(
    _t("Describe the email you want to send:"),
    value=st.session_state.user_prompt,
    placeholder=_t("e.g., 'An invitation to our annual charity gala, highlighting guest speaker Jane Doe and live music.'"),
    height=100
)
st.session_state.user_email_context = st.text_area(
    _t("Optional: Provide context about your email style or content preferences..."),
    value=st.session_state.user_email_context,
    placeholder=_t("e.g., 'I prefer concise, direct language and a friendly tone.'"),
    height=80
)
st.session_state.personalize_emails = st.checkbox(
    _t("Personalize each email (uses contact name and makes it unique)"),
    value=st.session_state.personalize_emails
)

# --- Email Generation ---
st.header(_t("Generate Emails"))

if st.button(_t("Generate Emails for Contacts")):
    if not st.session_state.contacts:
        st.error(_t("Please upload an Excel file with contacts first."))
    elif not st.session_state.user_prompt:
        st.error(_t("Please provide a description for the email."))
    elif not OPENAI_API_KEY:
        st.error(_t("OpenAI API Key not found. Cannot generate emails."))
    else:
        st.session_state.generated_emails = []
        
        # Initialize the AI agent
        try:
            agent = SmartEmailAgent(openai_api_key=OPENAI_API_KEY)
        except ValueError as e:
            st.error(f"{_t('Error initializing AI agent: ')}{e}. {_t('Please check your OpenAI API Key.')}")
            st.stop()

        generation_progress_bar = st.progress(0, text=_t("Generating emails..."))
        for i, contact in enumerate(st.session_state.contacts):
            email_output = agent.generate_email(
                prompt=st.session_state.user_prompt,
                contact_name=contact['name'],
                personalize=st.session_state.personalize_emails,
                user_email_context=st.session_state.user_email_context,
                output_language=st.session_state.language # Pass the selected language
            )
            st.session_state.generated_emails.append({
                "name": contact['name'],
                "email": contact['email'],
                "subject": email_output['subject'],
                "body": email_output['body']
            })
            generation_progress_bar.progress((i + 1) / len(st.session_state.contacts), text=f"{_t('Generating email for ')}{contact['name']}...")
        
        generation_progress_bar.empty()
        st.success(f"{_t('Generated ')}{len(st.session_state.generated_emails)}{_t(' emails!')}")
        st.session_state.show_preview = True

# --- Email Sending Logic ---
st.header(_t("Send Emails"))

if st.session_state.generated_emails:
    col1, col2 = st.columns([1, 1])

    with col1:
        st.write(f"{_t('You are about to send emails to')} **{len(st.session_state.generated_emails)}**{_t(' contacts.')}")
        st.write(f"**{_t('Sending Mode:')}** {'**' + _t('FULLY PERSONALIZED') + '**' if st.session_state.personalize_emails else '**' + _t('TEMPLATE-BASED') + '**'}")

        selected_sender_password = SENDER_PASSWORD

        if not selected_sender_password:
            st.error(f"{_t('Error: Password not found for sender email:')} `{SENDER_EMAIL}`. {_t('Please check your Streamlit Secrets.')}")
        else:
            if st.button(_t("Confirm Send All Emails"), key="confirm_send_button"):
                st.write(_t("--- Sending Emails ---"))
                success_count = 0
                failed_or_skipped_count = 0
                st.session_state.email_sending_status = []

                send_progress_bar = st.progress(0, text=_t("Sending emails..."))

                temp_dir = None
                attachment_paths = []

                if st.session_state.uploaded_attachments:
                    try:
                        temp_dir = tempfile.mkdtemp()
                        st.session_state.email_sending_status.append(f"{_t('Preparing ')}{len(st.session_state.uploaded_attachments)}{_t(' attachment(s)...')}")

                        for uploaded_file in st.session_state.uploaded_attachments:
                            file_path = os.path.join(temp_dir, uploaded_file.name)
                            with open(file_path, "wb") as f:
                                f.write(uploaded_file.getbuffer())
                            attachment_paths.append(file_path)
                        st.session_state.email_sending_status.append(_t("Attachments prepared."))
                        print(f"CONSOLE LOG: streamlit_app.py: Attachments saved to temporary directory: {temp_dir}")
                    except Exception as e:
                        st.session_state.email_sending_status.append(f"{_t('ERROR: Could not prepare attachments: ')}{e}")
                        st.error(f"{_t('Could not prepare attachments: ')}{e}. {_t('Email sending aborted.')}")
                        send_progress_bar.empty()
                        if temp_dir and os.path.exists(temp_dir):
                            try: shutil.rmtree(temp_dir)
                            except Exception as cleanup_e: print(f"Cleanup error: {cleanup_e}")
                        st.stop()

                try:
                    for i, email_data in enumerate(st.session_state.generated_emails):
                        st.session_state.email_sending_status.append(f"{_t('Attempting to send email to ')}{email_data['name']} ({email_data['email']})...")
                        st.empty().write("\n".join(st.session_state.email_sending_status[-5:]))

                        result = send_email_message(
                            sender_email=selected_sender_email,
                            sender_password=selected_sender_password,
                            to_email=email_data['email'],
                            subject=email_data['subject'],
                            body=email_data['body'],
                            attachments=attachment_paths,
                            log_path=FAILED_EMAILS_LOG_PATH # Pass the log path
                        )

                        if result["status"] == "success":
                            st.session_state.email_sending_status.append(f"{_t('Email sent successfully to ')}{email_data['name']}.")
                            success_count += 1
                        else:
                            st.session_state.email_sending_status.append(f"{_t('Failed to send email to ')}{email_data['name']}: {result['message']}")
                            failed_or_skipped_count += 1

                        send_progress_bar.progress((i + 1) / len(st.session_state.generated_emails))

                    st.session_state.email_sending_status.append(_t("--- Sending Complete ---"))
                    st.success(_t("All emails processed!"))
                    st.session_state.email_sending_status.append(f"{_t('Total contacts processed:')} {len(st.session_state.generated_emails)}")
                    st.session_state.email_sending_status.append(f"{_t('Successful emails sent:')} {success_count}")
                    st.session_state.email_sending_status.append(f"{_t('Failed or Skipped emails:')} {failed_or_skipped_count}")

                finally:
                    send_progress_bar.empty()
                    if temp_dir and os.path.exists(temp_dir):
                        try:
                            shutil.rmtree(temp_dir)
                            st.session_state.email_sending_status.append(_t("Temporary attachments cleaned up."))
                            print(f"CONSOLE LOG: streamlit_app.py: Cleaned up temporary directory: {temp_dir}")
                        except Exception as cleanup_e:
                            st.session_state.email_sending_status.append(f"{_t('ERROR: Could not clean up temporary attachments: ')}{cleanup_e}")
                            print(f"ERROR: streamlit_app.py: Could not clean up temporary directory {temp_dir}: {cleanup_e}")

                st.markdown("---")
                st.subheader(_t("Activity Log"))
                for log_entry in reversed(st.session_state.email_sending_status):
                    st.write(log_entry)
                
                if st.button(_t("Start New Email Session")):
                    for key in st.session_state.keys():
                        del st.session_state[key]
                    st.rerun()

    with col2:
        if st.session_state.show_preview and st.session_state.generated_emails:
            st.subheader(_t("Preview Email Content"))
            st.warning(_t("This is a preview of the FIRST email generated. The content will vary if 'Personalize Emails' is checked."))
            preview_email = st.session_state.generated_emails[0]
            st.markdown(f"**{_t('From:')}** `{selected_sender_email}`")
            st.markdown(f"**{_t('To:')}** `{preview_email['name']} <{preview_email['email']}>`")
            st.markdown(f"**{_t('Subject:')}** `{preview_email['subject']}`")
            st.markdown("---")
            st.markdown(preview_email['body'])
            st.markdown("---")

else:
    st.info(_t("Upload an Excel file and generate emails to see the sending options.")) # TRADUIT