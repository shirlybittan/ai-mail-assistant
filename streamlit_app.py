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
from translations import LANGUAGES, _t

# --- Streamlit Page Configuration ---
st.set_page_config(layout="wide", page_title=_t("AI Email Assistant"))

# --- Global Variables / Access from config (defined at top scope) ---
selected_sender_email = SENDER_EMAIL
selected_sender_password = SENDER_PASSWORD

# --- Session State Initialization ---
# Ensure language is set BEFORE the selectbox is rendered
if 'language' not in st.session_state:
    st.session_state.language = "fr" # Default language set to French

if 'page' not in st.session_state:
    st.session_state.page = 'generate' # Initial page

# Core data states
if 'contacts' not in st.session_state:
    st.session_state.contacts = []
if 'contact_issues' not in st.session_state:
    st.session_state.contact_issues = []
if 'uploaded_attachments' not in st.session_state:
    st.session_state.uploaded_attachments = []
if 'personalize_emails' not in st.session_state:
    st.session_state.personalize_emails = False
if 'user_prompt' not in st.session_state:
    st.session_state.user_prompt = ""
if 'user_email_context' not in st.session_state:
    st.session_state.user_email_context = ""
if 'generic_greeting' not in st.session_state: # New state for generic greeting
    st.session_state.generic_greeting = ""


# States for generated content
if 'generated_personalized_emails' not in st.session_state: # List of fully personalized emails (if mode is personalized)
    st.session_state.generated_personalized_emails = []
if 'template_email' not in st.session_state: # Single template email (if mode is template-based)
    st.session_state.template_email = None # Stores {"subject": "...", "body": "..."} with {{Name}}
if 'editable_preview_subject' not in st.session_state: # Subject as seen/edited in preview
    st.session_state.editable_preview_subject = ""
if 'editable_preview_body' not in st.session_state: # Body as seen/edited in preview
    st.session_state.editable_preview_body = ""


# States for sending process
if 'email_sending_status' not in st.session_state:
    st.session_state.email_sending_status = []
if 'sending_in_progress' not in st.session_state:
    st.session_state.sending_in_progress = False


# --- Header & Language Selector ---
col_lang_select, _ = st.columns([0.2, 0.8])
with col_lang_select:
    # Find the index of "fr" to set it as default
    default_lang_index = list(LANGUAGES.keys()).index("fr") if "fr" in LANGUAGES else 0
    st.session_state.language = st.selectbox(
        label="Language",
        options=list(LANGUAGES.keys()),
        format_func=lambda x: LANGUAGES[x],
        key="language_selector",
        index=default_lang_index # Set default index
    )

# Customized and friendly main title
st.markdown("<h1 style='text-align: center; color: #0056b3; font-size: 2.5em; padding-bottom: 20px;'>📧 Assistant E-mail IA Professionnel</h1>", unsafe_allow_html=True)


# --- Navigation Buttons (Conditional Rendering based on page) ---
if st.session_state.page == 'preview':
    if st.button(_t("Back to Generation"), key="back_to_generation_preview"):
        st.session_state.page = 'generate'
        st.rerun()
elif st.session_state.page == 'sending_log':
    # This button allows going back to generation from the log page
    if st.button(_t("Back to Generation"), key="back_to_generation_log"):
        st.session_state.page = 'generate'
        st.rerun()
    # The "Start New Email Session" button is at the bottom of the sending_log page


# --- Page 1: Email Generation (Page 'generate') ---
if st.session_state.page == 'generate':
    # Removed st.header(_t("Configuration")) as requested

    # Check if sender credentials and OpenAI API key are loaded from config.py
    if not selected_sender_email or not selected_sender_password:
        st.error(_t("Sender email or password not found. Please configure them correctly in Streamlit Secrets under [app_credentials]."))
        st.stop()
    if not OPENAI_API_KEY:
        st.error(_t("OpenAI API Key not found. Cannot generate emails."))
        st.stop()

    st.info(f"{_t('Using sender email:')} **{selected_sender_email}**")


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

    # Generic greeting for non-personalized emails - now greyed out when personalize is checked
    generic_greeting_disabled = st.session_state.personalize_emails
    st.session_state.generic_greeting = st.text_input(
        _t("Optional Generic Greeting for Non-Personalized Emails:"),
        value=st.session_state.generic_greeting,
        placeholder=_t("e.g., 'Dear Valued Customer,', 'Hello Team,'"),
        disabled=generic_greeting_disabled # Make it greyed out
    )
    st.info(_t("This field is ignored if 'Personalize each email' is checked."))


    # Make the "Generate Emails" button more central and prominent
    st.markdown("---") # Add a separator for visual grouping
    col_gen_btn_1, col_gen_btn_2, col_gen_btn_3 = st.columns([1, 2, 1])
    with col_gen_btn_2:
        if st.button(_t("Generate Emails for Contacts"), type="primary", use_container_width=True):
            if not st.session_state.contacts:
                st.error(_t("Please upload an Excel file with contacts first."))
            elif not st.session_state.user_prompt:
                st.error(_t("Please provide a description for the email."))
            elif not OPENAI_API_KEY:
                st.error(_t("OpenAI API Key not found. Cannot generate emails."))
            else:
                st.session_state.generated_personalized_emails = [] # Clear previous list
                st.session_state.template_email = None # Clear previous template

                try:
                    agent = SmartEmailAgent(openai_api_key=OPENAI_API_KEY)
                except ValueError as e:
                    st.error(f"{_t('Error initializing AI agent: ')}{e}. {_t('Please check your OpenAI API Key.')}")
                    st.stop()

                if not st.session_state.personalize_emails:
                    # Generate a single template (faster for non-personalized)
                    with st.spinner(_t("Generating emails...")):
                        template_output = agent.generate_email(
                            prompt=st.session_state.user_prompt,
                            personalize=False, # Explicitly generate template with {{Name}}
                            user_email_context=st.session_state.user_email_context,
                            output_language=st.session_state.language
                        )

                    if "Error" in template_output["subject"]:
                        st.error(f"{_t('Error generating template email:')} {template_output['body']}")
                    else:
                        st.session_state.template_email = template_output
                        st.success(f"{_t('Generated ')}{1}{_t(' template email!')}") # Report 1 template generated

                        # --- Apply generic greeting to template for preview if applicable ---
                        # This logic is crucial for the preview
                        preview_body_content = st.session_state.template_email['body']
                        if st.session_state.generic_greeting:
                            # Replace {{Name}} in the template body with the generic greeting for preview
                            preview_body_content = preview_body_content.replace('{{Name}}', st.session_state.generic_greeting)
                        else:
                            # If no generic greeting, replace {{Name}} with 'Client' or a similar placeholder for better preview context
                            preview_body_content = preview_body_content.replace('{{Name}}', 'Client') # Default placeholder for preview

                        st.session_state.editable_preview_subject = st.session_state.template_email['subject']
                        st.session_state.editable_preview_body = preview_body_content # Set the modified body for preview

                        st.session_state.page = 'preview' # Move to preview page
                        st.rerun() # Rerun to scroll to top

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
                        st.session_state.generated_personalized_emails.append({
                            "name": contact['name'],
                            "email": contact['email'],
                            "subject": email_output['subject'],
                            "body": email_output['body']
                        })
                        generation_progress_bar.progress((i + 1) / len(st.session_state.contacts), text=f"{_t('Generating email for ')}{contact['name']}...")

                    generation_progress_bar.empty()
                    st.success(f"{_t('Generated ')}{len(st.session_state.generated_personalized_emails)}{_t(' emails!')} ({_t('FULLY PERSONALIZED')})")

                    if st.session_state.generated_personalized_emails:
                        # Set preview content to the first fully personalized email
                        first_email = st.session_state.generated_personalized_emails[0]
                        st.session_state.editable_preview_subject = first_email['subject']
                        st.session_state.editable_preview_body = first_email['body']
                        st.session_state.page = 'preview' # Move to preview page
                        st.rerun() # Rerun to scroll to top


# --- Page 2: Email Content Preview & Send (Page 'preview') ---
elif st.session_state.page == 'preview':
    # Re-calculate preview content each time the page loads to ensure freshness
    # This block ensures that editable_preview_subject and editable_preview_body
    # always reflect the latest state based on personalized_emails or template_email
    # and the generic_greeting, ensuring the correct salutation is shown.
    preview_subject_initial = ""
    preview_body_initial = ""
    preview_name_display = ""

    if st.session_state.personalize_emails and st.session_state.generated_personalized_emails:
        first_email = st.session_state.generated_personalized_emails[0]
        preview_subject_initial = first_email['subject']
        preview_body_initial = first_email['body']
        preview_name_display = first_email['name']
    elif st.session_state.template_email:
        preview_subject_initial = st.session_state.template_email['subject']
        # Ensure the body reflects the generic greeting or placeholder for preview
        temp_body = st.session_state.template_email['body']
        if st.session_state.generic_greeting:
            # Replace {{Name}} in the template body with the generic greeting for preview
            temp_body = temp_body.replace('{{Name}}', st.session_state.generic_greeting)
        else:
            temp_body = temp_body.replace('{{Name}}', 'Client') # Placeholder for preview if no generic greeting
        preview_body_initial = temp_body
        preview_name_display = "Template"

    # Update editable session states with freshly calculated values
    st.session_state.editable_preview_subject = preview_subject_initial
    st.session_state.editable_preview_body = preview_body_initial


    st.header(_t("Email Content Preview & Send"))

    if not (st.session_state.generated_personalized_emails or st.session_state.template_email):
        st.warning(_t("Please generate emails first."))
    else:
        # Information about the preview mode (template vs. personalized)
        if not st.session_state.personalize_emails:
            if not st.session_state.generic_greeting: # If no generic greeting was provided
                st.info(_t("This email is a template. The '{{Name}}' placeholder will be replaced with each contact's name."))
            else: # If generic greeting was provided
                st.info(f"{_t('This email is a template. The greeting has been set to:')} **{st.session_state.generic_greeting}**")
        st.warning(_t("This is a preview of the FIRST email generated. The content will vary if 'Personalize Emails' is checked."))

        # Display editable subject and body
        st.session_state.editable_preview_subject = st.text_input(
            _t("Subject:"), value=st.session_state.editable_preview_subject, # Use the re-calculated value
            key="editable_subject"
        )

        st.markdown(f"**{_t('Email Body:')}**")
        st.session_state.editable_preview_body = st.text_area(
            "", value=st.session_state.editable_preview_body, # Use the re-calculated value
            height=400,
            key="editable_body"
        )

        st.markdown("---") # Separator before attachments and send button

        # --- Add attachments on preview page ---
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
            key="attachment_uploader_preview_page"
        )

        if st.session_state.uploaded_attachments:
            st.info(f"{len(st.session_state.uploaded_attachments)}{_t(' file(s) selected for attachment.')}")
        st.markdown("---") # Separator after attachments

        # --- Send All Emails Section (Simplified) ---
        # Simplified message
        sending_mode_text = _t('FULLY PERSONALIZED') if st.session_state.personalize_emails else _t('BASÉ SUR UN MODÈLE')
        st.write(f"{_t('Send emails to')} **{len(st.session_state.contacts)}** {_t('contacts')} ({sending_mode_text})")

        # Centralized and prominent send button
        col_send_btn_1, col_send_btn_2, col_send_btn_3 = st.columns([1, 2, 1])
        with col_send_btn_2:
            if not selected_sender_password: # Use selected_sender_password from global scope
                st.error(f"{_t('Error: Password not found for sender email:')} `{selected_sender_email}`. {_t('Please check your Streamlit Secrets.')}")
            else:
                if st.button(_t("Confirm and Send"), type="primary", use_container_width=True, key="confirm_send_button"):
                    st.session_state.email_sending_status = [] # Clear previous status log
                    st.session_state.sending_in_progress = True # Indicate sending has started

                    final_emails_to_send = []
                    if not st.session_state.personalize_emails:
                        # Build the full list of emails for sending based on the edited template
                        # The editable_preview_body already contains the generic greeting if set (or 'Client' placeholder).
                        for contact in st.session_state.contacts:
                            body_for_sending = st.session_state.editable_preview_body

                            # Always ensure {{Name}} (if it somehow slipped through) or 'Client' placeholder is replaced by the actual contact name for SENDING
                            if '{{Name}}' in body_for_sending:
                                body_for_sending = body_for_sending.replace('{{Name}}', contact['name'])
                            elif st.session_state.generic_greeting:
                                # If generic greeting was used for preview, ensure it's still there
                                # No replacement needed if generic greeting already applied for preview
                                pass
                            else:
                                # If 'Client' was used as a placeholder in preview, replace it with the actual name for sending
                                body_for_sending = body_for_sending.replace('Client', contact['name'])


                            final_emails_to_send.append({
                                "name": contact['name'],
                                "email": contact['email'],
                                "subject": st.session_state.editable_preview_subject,
                                "body": body_for_sending # Use the body prepared for sending
                            })
                    else:
                        # For personalized mode, take the generated list and apply edits from the preview for the first email
                        final_emails_to_send = st.session_state.generated_personalized_emails[:] # Make a copy
                        if final_emails_to_send: # Ensure there's at least one email
                            final_emails_to_send[0]['subject'] = st.session_state.editable_preview_subject
                            final_emails_to_send[0]['body'] = st.session_state.editable_preview_body

                    if not final_emails_to_send:
                        st.error(_t("No emails to send. Please ensure contacts are loaded and emails generated."))
                        st.session_state.sending_in_progress = False # Reset sending flag
                        st.stop() # Stop execution if nothing to send

                    # Store the final list of emails to be sent in session state
                    st.session_state.final_emails_to_send = final_emails_to_send

                    # Switch to the sending_log page and trigger rerun
                    st.session_state.page = 'sending_log'
                    st.session_state.email_sending_status.append(_t("--- Sending Emails ---"))
                    st.session_state.email_sending_status.append(f"{_t('You are about to send emails to')} {len(st.session_state.final_emails_to_send)} {_t('contacts.')}")
                    st.rerun()


# --- Page 3: Sending Activity Log (Page 'sending_log') ---
elif st.session_state.page == 'sending_log':
    st.header(_t("Sending Activity Log"))

    # Only run the sending logic once when entering this page
    if st.session_state.sending_in_progress:
        success_count = 0
        failed_or_skipped_count = 0

        # Retrieve the emails to send from session state
        final_emails_to_send = st.session_state.final_emails_to_send

        if not final_emails_to_send:
            st.error(_t("No emails found to send. This shouldn't happen."))
            st.session_state.sending_in_progress = False
        else:
            send_progress_bar = st.progress(0, text=_t("Sending emails..."))

            temp_dir = None
            attachment_paths = []

            if st.session_state.uploaded_attachments:
                try:
                    temp_dir = tempfile.mkdtemp()
                    st.session_state.email_sending_status.append(f"{_t('Preparing ')}{len(st.session_state.uploaded_attachments)}{_t(' attachment(s)...')}")
                    st.empty().write("\n".join(st.session_state.email_sending_status)) # Update log in real-time

                    for uploaded_file in st.session_state.uploaded_attachments:
                        file_path = os.path.join(temp_dir, uploaded_file.name)
                        with open(file_path, "wb") as f:
                            f.write(uploaded_file.getbuffer())
                        attachment_paths.append(file_path)
                    st.session_state.email_sending_status.append(_t("Attachments prepared."))
                    st.empty().write("\n".join(st.session_state.email_sending_status)) # Update log in real-time
                    print(f"CONSOLE LOG: streamlit_app.py: Attachments saved to temporary directory: {temp_dir}")
                except Exception as e:
                    st.session_state.email_sending_status.append(f"{_t('ERROR: Could not prepare attachments: ')}{e}")
                    st.error(f"{_t('Could not prepare attachments: ')}{e}. {_t('Email sending aborted.')}")
                    send_progress_bar.empty()
                    if temp_dir and os.path.exists(temp_dir):
                        try: shutil.rmtree(temp_dir)
                        except Exception as cleanup_e: print(f"Cleanup error: {cleanup_e}")
                    st.session_state.sending_in_progress = False
                    # Update status log in UI
                    st.empty().write("\n".join(st.session_state.email_sending_status))
                    # st.stop() # Removed st.stop() to allow displaying final log

            try:
                for i, email_data in enumerate(final_emails_to_send):
                    status_message = f"{_t('Attempting to send email to ')}{email_data['name']} ({email_data['email']})..."
                    st.session_state.email_sending_status.append(status_message)
                    # Displaying only the last few status updates to keep the UI clean
                    st.empty().write("\n".join(st.session_state.email_sending_status[-5:]))

                    result = send_email_message(
                        sender_email=selected_sender_email,
                        sender_password=selected_sender_password,
                        to_email=email_data['email'],
                        subject=email_data['subject'],
                        body=email_data['body'],
                        attachments=attachment_paths,
                        log_path=FAILED_EMAILS_LOG_PATH
                    )

                    if result["status"] == "success":
                        st.session_state.email_sending_status.append(f"{_t('Email sent successfully to ')}{email_data['name']}.")
                        success_count += 1
                    else:
                        st.session_state.email_sending_status.append(f"{_t('Failed to send email to ')}{email_data['name']}: {result['message']}")
                        failed_or_skipped_count += 1

                    send_progress_bar.progress((i + 1) / len(final_emails_to_send))
                    st.empty().write("\n".join(st.session_state.email_sending_status[-5:])) # Update log in real-time

                st.session_state.email_sending_status.append(_t("--- Sending Complete ---"))
                st.success(_t("All emails processed!"))
                st.session_state.email_sending_status.append(f"{_t('Total contacts processed:')} {len(final_emails_to_send)}")
                st.session_state.email_sending_status.append(f"{_t('Successful emails sent:')} {success_count}")
                st.session_state.email_sending_status.append(f"{_t('Failed or Skipped emails:')} {failed_or_skipped_count}")

            finally:
                send_progress_bar.empty()
                st.session_state.sending_in_progress = False # Mark sending as complete
                if temp_dir and os.path.exists(temp_dir):
                    try:
                        shutil.rmtree(temp_dir)
                        st.session_state.email_sending_status.append(_t("Temporary attachments cleaned up."))
                        print(f"CONSOLE LOG: streamlit_app.py: Cleaned up temporary directory: {temp_dir}")
                    except Exception as cleanup_e:
                        st.session_state.email_sending_status.append(f"{_t('ERROR: Could not clean up temporary attachments: ')}{cleanup_e}")
                        print(f"ERROR: streamlit_app.py: Could not clean up temporary directory {temp_dir}: {cleanup_e}")

                # Final display of the complete log
                st.empty().write("\n".join(st.session_state.email_sending_status))


    # Display the activity log once sending is finished or if it was already finished
    st.markdown("---")
    st.subheader(_t("Activity Log"))
    # Always show the full log at the end
    for log_entry in reversed(st.session_state.email_sending_status):
        st.write(log_entry)

    if not st.session_state.sending_in_progress: # Only show 'Start New' button when sending is done
        if st.button(_t("Start New Email Session")):
            # Reset all relevant session state variables for a fresh start
            for key in [
                'generated_personalized_emails', 'template_email', 'email_sending_status',
                'uploaded_attachments', 'contacts', 'contact_issues',
                'user_prompt', 'user_email_context', 'personalize_emails',
                'editable_preview_subject', 'editable_preview_body', 'sending_in_progress',
                'generic_greeting', 'final_emails_to_send'
            ]:
                if key in st.session_state:
                    del st.session_state[key]
            st.session_state.page = 'generate' # Go back to the first page
            st.rerun()