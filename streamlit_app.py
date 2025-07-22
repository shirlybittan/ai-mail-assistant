# streamlit_app.py

import streamlit as st
import pandas as pd
from data_handler import load_contacts_from_excel
from email_generator import SmartEmailAgent
from email_tool import send_email_message
from config import SENDER_CREDENTIALS, OPENAI_API_KEY, SENDER_EMAIL, SENDER_PASSWORD, FAILED_EMAILS_LOG_PATH
import tempfile
import os
import shutil
import datetime

# --- IMPORT LANGUAGE HELPER ---
from translations import LANGUAGES, _t # Import LANGUAGES for selectbox options, and _t for translation


# --- Streamlit Page Configuration ---
st.set_page_config(layout="wide", page_title=_t("AI Email Assistant"))

# --- Session State Initialization ---
if 'language' not in st.session_state:
    st.session_state.language = "fr" # Default language set to French

if 'page' not in st.session_state:
    st.session_state.page = 'generate' # Initial page

if 'generated_emails' not in st.session_state:
    st.session_state.generated_emails = []
if 'email_sending_status' not in st.session_state:
    st.session_state.email_sending_status = []
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
if 'editable_preview_subject' not in st.session_state:
    st.session_state.editable_preview_subject = ""
if 'editable_preview_body' not in st.session_state:
    st.session_state.editable_preview_body = ""


# --- Language Selector (Top Right) ---
col_lang_select, _ = st.columns([0.2, 0.8])
with col_lang_select:
    st.session_state.language = st.selectbox(
        label="Language",
        options=list(LANGUAGES.keys()),
        format_func=lambda x: LANGUAGES[x],
        key="language_selector"
    )

st.title(f"📧 {_t('AI Email Assistant')}")

# --- DEBUGGING INFO (REMOVABLE) ---
# st.subheader(_t("Debugging Info (REMOVE AFTER TROUBLESHOOTING)"))
# st.write(f"{_t('All secrets from st.secrets:')}", st.secrets.to_dict())
# st.write(f"{_t('Sender credentials (from config):')}", SENDER_CREDENTIALS)
# st.write(f"{_t('OpenAI key (from config):')}", OPENAI_API_KEY)
# st.write(f"{_t('DEBUG: SENDER_EMAIL retrieved:')}", SENDER_EMAIL)
# st.write(f"{_t('DEBUG: SENDER_PASSWORD present:')}", bool(SENDER_PASSWORD))
# st.write(f"{_t('DEBUG: FAILED_EMAILS_LOG_PATH:')}", FAILED_EMAILS_LOG_PATH)
# st.markdown("---")


# --- Navigation Buttons ---
if st.session_state.page == 'generate':
    pass # No "Back" button on the first page
elif st.session_state.page == 'preview':
    if st.button(_t("Back to Generation")):
        st.session_state.page = 'generate'
        st.rerun()
elif st.session_state.page == 'send':
    if st.button(_t("Back to Generation")): # Back to generation from send page
        st.session_state.page = 'generate'
        st.rerun()


# --- Page: Email Generation ---
if st.session_state.page == 'generate':
    st.header(_t("Configuration"))

    # Check if sender credentials and OpenAI API key are loaded from config.py
    if not SENDER_EMAIL or not SENDER_PASSWORD:
        st.error(_t("Sender email or password not found. Please configure them correctly in Streamlit Secrets under [app_credentials]."))
        st.stop()
    if not OPENAI_API_KEY:
        st.error(_t("OpenAI API Key not found. Please configure it correctly in Streamlit Secrets under [app_credentials]."))
        st.stop()

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

            try:
                agent = SmartEmailAgent(openai_api_key=OPENAI_API_KEY)
            except ValueError as e:
                st.error(f"{_t('Error initializing AI agent: ')}{e}. {_t('Please check your OpenAI API Key.')}")
                st.stop()

            # --- OPTIMIZED GENERATION LOGIC ---
            if not st.session_state.personalize_emails:
                # Generate a single template if not personalizing
                with st.spinner(_t("Generating emails...")):
                    template_output = agent.generate_email(
                        prompt=st.session_state.user_prompt,
                        personalize=False, # Explicitly generate template
                        user_email_context=st.session_state.user_email_context,
                        output_language=st.session_state.language
                    )

                if "Error" in template_output["subject"]:
                    st.error(f"{_t('Error generating template email:')} {template_output['body']}")
                else:
                    # Apply template to all contacts
                    for contact in st.session_state.contacts:
                        # Replace {{Name}} placeholder with actual name
                        personalized_body = template_output['body'].replace('{{Name}}', contact['name'])
                        st.session_state.generated_emails.append({
                            "name": contact['name'],
                            "email": contact['email'],
                            "subject": template_output['subject'],
                            "body": personalized_body
                        })
                    st.success(f"{_t('Generated ')}{len(st.session_state.generated_emails)}{_t(' emails!')} ({_t('TEMPLATE-BASED')})")

            else:
                # Generate individually if personalizing
                generation_progress_bar = st.progress(0, text=_t("Generating emails..."))
                for i, contact in enumerate(st.session_state.contacts):
                    email_output = agent.generate_email(
                        prompt=st.session_state.user_prompt,
                        contact_name=contact['name'],
                        personalize=True,
                        user_email_context=st.session_state.user_email_context,
                        output_language=st.session_state.language
                    )
                    st.session_state.generated_emails.append({
                        "name": contact['name'],
                        "email": contact['email'],
                        "subject": email_output['subject'],
                        "body": email_output['body']
                    })
                    generation_progress_bar.progress((i + 1) / len(st.session_state.contacts), text=f"{_t('Generating email for ')}{contact['name']}...")

                generation_progress_bar.empty()
                st.success(f"{_t('Generated ')}{len(st.session_state.generated_emails)}{_t(' emails!')} ({_t('FULLY PERSONALIZED')})")

            # After generation, move to preview page
            if st.session_state.generated_emails:
                first_email = st.session_state.generated_emails[0]
                st.session_state.editable_preview_subject = first_email['subject']
                st.session_state.editable_preview_body = first_email['body']
                st.session_state.page = 'preview'
                st.rerun()


# --- Page: Email Preview & Edit ---
elif st.session_state.page == 'preview':
    st.header(_t("Email Content Preview & Edit"))

    if not st.session_state.generated_emails:
        st.warning(_t("Please generate emails first."))
        if st.button(_t("Back to Generation")):
            st.session_state.page = 'generate'
            st.rerun()
    else:
        # Display editable subject and body
        st.subheader(f"{_t('Preview for ')}{st.session_state.generated_emails[0]['name']}")
        if not st.session_state.personalize_emails:
            st.info(_t("This email is a template. The '{{Name}}' placeholder will be replaced with each contact's name."))
        st.warning(_t("This is a preview of the FIRST email generated. The content will vary if 'Personalize Emails' is checked."))

        edited_subject = st.text_input(_t("Subject:"), value=st.session_state.editable_preview_subject)
        edited_body = st.text_area(_t("Email Body:"), value=st.session_state.editable_preview_body, height=400)

        # Update session state with edited content
        st.session_state.editable_preview_subject = edited_subject
        st.session_state.editable_preview_body = edited_body

        if st.button(_t("Proceed to Send Emails")):
            # If template-based, apply edits to all generated emails
            if not st.session_state.personalize_emails:
                for email_data in st.session_state.generated_emails:
                    email_data['subject'] = edited_subject
                    # Re-apply placeholder substitution in case body was edited
                    email_data['body'] = edited_body.replace('{{Name}}', email_data['name'])
            else:
                # If personalized, the user edits the first email, but for sending,
                # we'd typically use the *originally* generated personalized emails.
                # If the user edits, this implies they want the first email to be this edited version,
                # and if they proceed, the others remain as originally personalized.
                # For simplicity here, if personalized, only the first one is shown/edited.
                # If you want to apply edits to *all* personalized emails, it would require
                # re-generating or re-applying changes based on a diff, which is complex.
                # For now, we'll assume the edit is primarily for the first preview,
                # and send uses the original if not template-based.
                # Let's re-evaluate if the user edits a personalized email and wants that specific edit for all.
                # For now, to keep it simple, if `personalize_emails` is True, this edit applies only to the first email in the list.
                # If this is not desired, we'd need to deep copy and apply edits selectively.
                # To be consistent with "preview of the first email", let's update the first email's content.
                if st.session_state.generated_emails:
                    st.session_state.generated_emails[0]['subject'] = edited_subject
                    st.session_state.generated_emails[0]['body'] = edited_body


            st.session_state.page = 'send'
            st.rerun()


# --- Page: Email Sending ---
elif st.session_state.page == 'send':
    st.header(_t("Send Emails"))

    if not st.session_state.generated_emails:
        st.warning(_t("Please generate or load emails to send."))
        if st.button(_t("Back to Generation")):
            st.session_state.page = 'generate'
            st.rerun()
    else:
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
                        # Displaying only the last 5 status updates to keep the UI clean
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
                    # Reset all relevant session state variables
                    for key in [
                        'generated_emails', 'email_sending_status', 'uploaded_attachments',
                        'contacts', 'contact_issues', 'user_prompt', 'user_email_context',
                        'personalize_emails', 'page', 'editable_preview_subject', 'editable_preview_body'
                    ]:
                        if key in st.session_state:
                            del st.session_state[key]
                    st.rerun()