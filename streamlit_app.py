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
if 'template_email' not in st.session_state:
    st.session_state.template_email = {"recipient": "", "subject": "", "body": "", "sender": selected_sender_email}
if 'generated_personalized_emails' not in st.session_state:
    st.session_state.generated_personalized_emails = []
if 'email_sending_status' not in st.session_state:
    st.session_state.email_sending_status = [] # To log status of each email sent
if 'sending_in_progress' not in st.session_state:
    st.session_state.sending_in_progress = False # Flag to prevent re-triggering send
if 'editable_preview_subject' not in st.session_state:
    st.session_state.editable_preview_subject = ""
if 'editable_preview_body' not in st.session_state:
    st.session_state.editable_preview_body = ""
if 'generic_greeting' not in st.session_state:
    st.session_state.generic_greeting = ""
if 'final_emails_to_send' not in st.session_state:
    st.session_state.final_emails_to_send = [] # Stores emails after final review


# --- Helper Function for Translation (defined after session state for language) ---
# Set the global language based on session state BEFORE using _t for page title etc.
# This ensures that _t uses the correct language from session_state immediately.
from translations import set_language
set_language(st.session_state.language)


# --- Language Selector ---
st.sidebar.title(_t("AI Email Assistant"))
st.sidebar.image("AI.png", use_column_width=True) # Ensure this path is correct
selected_language = st.sidebar.selectbox(
    _t("Select your language"),
    options=list(LANGUAGES.keys()),
    format_func=lambda x: LANGUAGES[x],
    key="language_selector", # Use a key to prevent "DuplicateWidgetID" error
    index=list(LANGUAGES.keys()).index(st.session_state.language)
)

# Update session state and re-run if language changes
if selected_language != st.session_state.language:
    st.session_state.language = selected_language
    set_language(selected_language) # Update the global helper as well
    st.experimental_rerun()


# --- Navigation ---
st.sidebar.markdown("---")
if st.sidebar.button(_t("Generate Email"), key="nav_generate"):
    st.session_state.page = 'generate'
if st.sidebar.button(_t("Review & Send"), key="nav_review"):
    st.session_state.page = 'review'
st.sidebar.markdown("---")


# --- Page: Generate Email ---
if st.session_state.page == 'generate':
    st.header(_t("Generate Email"))
    st.write(_t("Compose your email details below."))

    # User input for email context and prompt
    st.session_state.user_prompt = st.text_area(_t("Describe the purpose of your email and what you want to achieve (e.g., 'send a personalized thank you email to customers who attended our webinar'):"), value=st.session_state.get('user_prompt', ''), height=100)
    st.session_state.user_email_context = st.text_area(_t("Provide additional context or key information to include in the email (e.g., 'Webinar Name: AI for Business, Date: 2024-07-20, Key speaker: Dr. Emily Chen'):"), value=st.session_state.get('user_email_context', ''), height=150)

    st.session_state.generic_greeting = st.text_input(_t("Generic Greeting (e.g., 'Dear Attendee', 'Hello'):"), value=st.session_state.get('generic_greeting', ''))

    st.session_state.personalize_emails = st.checkbox(_t("Personalize emails using contact data (e.g., recipient name)?"), value=st.session_state.get('personalize_emails', True))

    # File uploader for contacts
    uploaded_file = st.file_uploader(_t("Upload Contacts Excel File (optional, for personalization)"), type=["xlsx", "xls"])
    if uploaded_file is not None:
        try:
            contacts_df, issues = load_contacts_from_excel(uploaded_file)
            st.session_state.contacts = contacts_df.to_dict('records') # Store as list of dicts
            st.session_state.contact_issues = issues
            st.success(_t("Contacts loaded successfully."))

            if issues:
                st.warning(_t("Issues detected with some contacts:"))
                for issue in issues:
                    st.write(f"- {issue}")

            st.write(f"{_t('Loaded')} {len(st.session_state.contacts)} {_t('contacts.')}")
            st.dataframe(contacts_df.head())

        except Exception as e:
            st.error(f"{_t('Error loading contacts:')} {e}")

    # File uploader for attachments
    new_attachments = st.file_uploader(_t("Upload Attachments (optional)"), type=["pdf", "docx", "jpg", "png", "xlsx"], accept_multiple_files=True)
    if new_attachments:
        for attachment in new_attachments:
            # Check if the file is already in the list (simple name check for now)
            if not any(a.name == attachment.name for a in st.session_state.uploaded_attachments):
                st.session_state.uploaded_attachments.append(attachment)
        st.info(f"{_t('Total attachments queued:')} {len(st.session_state.uploaded_attachments)}")

    if st.session_state.uploaded_attachments:
        st.subheader(_t("Current Attachments:"))
        for i, attachment in enumerate(st.session_state.uploaded_attachments):
            col1, col2 = st.columns([0.8, 0.2])
            with col1:
                st.write(attachment.name)
            with col2:
                if st.button(_t("Remove"), key=f"remove_attachment_{i}"):
                    st.session_state.uploaded_attachments.pop(i)
                    st.experimental_rerun() # Rerun to update the list immediately

    if st.button(_t("Generate Email Template")):
        if not st.session_state.user_prompt:
            st.warning(_t("Please describe the purpose of your email to generate a template."))
        else:
            with st.spinner(_t("Generating email template...")):
                email_agent = SmartEmailAgent(api_key=OPENAI_API_KEY)
                try:
                    # Pass contact data for better context, even if not personalizing individual emails yet
                    template = email_agent.generate_email_template(
                        user_prompt=st.session_state.user_prompt,
                        email_context=st.session_state.user_email_context,
                        contacts_data=st.session_state.contacts if st.session_state.personalize_emails else []
                    )
                    st.session_state.template_email = {
                        "recipient": template.get("recipient", "placeholder@example.com"),
                        "subject": template.get("subject", ""),
                        "body": template.get("body", ""),
                        "sender": selected_sender_email
                    }
                    st.session_state.editable_preview_subject = st.session_state.template_email["subject"]
                    st.session_state.editable_preview_body = st.session_state.template_email["body"]
                    st.success(_t("Email template generated! Review and customize below."))
                except Exception as e:
                    st.error(f"{_t('Error generating email template:')} {e}")

    st.markdown("---")
    st.subheader(_t("Email Template Preview (Editable)"))

    st.session_state.editable_preview_subject = st.text_input(
        _t("Subject"),
        value=st.session_state.editable_preview_subject,
        key="preview_subject"
    )
    st.session_state.editable_preview_body = st.text_area(
        _t("Body"),
        value=st.session_state.editable_preview_body,
        height=300,
        key="preview_body"
    )

    if st.button(_t("Update Template & Go to Review")):
        st.session_state.template_email["subject"] = st.session_state.editable_preview_subject
        st.session_state.template_email["body"] = st.session_state.editable_preview_body
        st.session_state.page = 'review'
        st.experimental_rerun()


# --- Page: Review & Send ---
elif st.session_state.page == 'review':
    st.header(_t("Review & Send Emails"))
    st.write(_t("Review the generated emails and send them out."))

    if not st.session_state.template_email["subject"] or not st.session_state.template_email["body"]:
        st.warning(_t("Please go to 'Generate Email' tab and create an email template first."))
    else:
        st.subheader(_t("Base Email Template:"))
        st.text_input(_t("Subject"), value=st.session_state.template_email["subject"], disabled=True)
        st.text_area(_t("Body"), value=st.session_state.template_email["body"], height=200, disabled=True)
        st.write(f"{_t('Sender:')} {st.session_state.template_email['sender']}")

        st.markdown("---")

        if st.button(_t("Generate Personalized Emails for Review"), key="generate_for_review_btn"):
            if not st.session_state.contacts and st.session_state.personalize_emails:
                st.warning(_t("No contacts uploaded for personalization. Please upload contacts or uncheck 'Personalize emails'."))
            else:
                with st.spinner(_t("Personalizing emails...")):
                    email_agent = SmartEmailAgent(api_key=OPENAI_API_KEY)
                    try:
                        # Clear previous personalized emails
                        st.session_state.generated_personalized_emails = []
                        st.session_state.final_emails_to_send = []

                        if st.session_state.personalize_emails and st.session_state.contacts:
                            for i, contact in enumerate(st.session_state.contacts):
                                personalized_email = email_agent.personalize_email(
                                    template_subject=st.session_state.template_email["subject"],
                                    template_body=st.session_state.template_email["body"],
                                    contact_data=contact,
                                    user_prompt=st.session_state.user_prompt,
                                    generic_greeting=st.session_state.generic_greeting
                                )
                                # Add original recipient and mark for sending
                                personalized_email["to"] = contact.get("email", "unknown@example.com")
                                personalized_email["send"] = True # Default to sending
                                st.session_state.generated_personalized_emails.append(personalized_email)
                                st.session_state.final_emails_to_send.append(personalized_email) # Add to final list for sending

                            st.success(f"{_t('Generated')} {len(st.session_state.generated_personalized_emails)} {_t('personalized emails.')}")
                        else:
                            # If not personalizing or no contacts, use the template as a single email
                            single_email = {
                                "to": st.session_state.template_email["recipient"], # Placeholder or manually entered
                                "subject": st.session_state.template_email["subject"],
                                "body": st.session_state.template_email["body"],
                                "send": True # Default to sending
                            }
                            st.session_state.generated_personalized_emails = [single_email]
                            st.session_state.final_emails_to_send = [single_email]
                            st.info(_t("Using the base template as a single email since personalization is off or no contacts provided."))
                    except Exception as e:
                        st.error(f"{_t('Error personalizing emails:')} {e}")

        if st.session_state.generated_personalized_emails:
            st.subheader(_t("Emails for Review and Sending:"))
            if st.session_state.personalize_emails and st.session_state.contacts:
                st.info(_t("Review each email below. Uncheck the 'Send' box for any email you do not wish to send."))
            else:
                st.info(_t("Review the single email below."))


            for i, email_data in enumerate(st.session_state.generated_personalized_emails):
                with st.expander(f"{_t('Email to')} {email_data.get('to', _t('Unknown Recipient'))}", expanded=False):
                    email_to_send = next((item for item in st.session_state.final_emails_to_send if item.get("to") == email_data.get("to")), None)
                    if email_to_send:
                        # Use a unique key for each checkbox based on recipient and index
                        send_email_key = f"send_email_{email_data.get('to', '')}_{i}"
                        send_status = st.checkbox(_t("Send"), value=email_to_send["send"], key=send_email_key)
                        email_to_send["send"] = send_status # Update the actual object in final_emails_to_send

                    st.text_input(_t("Recipient"), value=email_data.get("to", ""), key=f"review_recipient_{i}", disabled=True)
                    st.text_input(_t("Subject"), value=email_data.get("subject", ""), key=f"review_subject_{i}", disabled=True)
                    st.text_area(_t("Body"), value=email_data.get("body", ""), height=200, key=f"review_body_{i}", disabled=True)


            if st.button(_t("Send Selected Emails Now"), disabled=st.session_state.sending_in_progress):
                st.session_state.sending_in_progress = True
                st.session_state.email_sending_status = [] # Clear previous logs
                st.info(_t("Sending emails... Please do not close this tab."))

                temp_dir = None
                try:
                    # Save attachments temporarily
                    if st.session_state.uploaded_attachments:
                        temp_dir = tempfile.mkdtemp()
                        attachment_paths = []
                        for uploaded_file in st.session_state.uploaded_attachments:
                            file_path = os.path.join(temp_dir, uploaded_file.name)
                            with open(file_path, "wb") as f:
                                f.write(uploaded_file.getbuffer())
                            attachment_paths.append(file_path)
                        st.session_state.email_sending_status.append(f"{_t('Attachments saved temporarily to:')} {temp_dir}")
                        print(f"Attachments saved temporarily to: {temp_dir}")
                    else:
                        attachment_paths = []

                    emails_to_actually_send = [e for e in st.session_state.final_emails_to_send if e["send"]]

                    if not emails_to_actually_send:
                        st.session_state.email_sending_status.append(_t("No emails selected for sending."))
                        st.warning(_t("No emails selected for sending."))
                    else:
                        for i, email_data in enumerate(emails_to_actually_send):
                            recipient = email_data.get("to")
                            subject = email_data.get("subject")
                            body = email_data.get("body")
                            sender = st.session_state.template_email["sender"]

                            if not recipient or not subject or not body:
                                status_message = f"{_t('SKIPPED (Missing Info): Email to')} {recipient or 'N/A'}"
                                st.session_state.email_sending_status.append(f"🔴 {status_message}")
                                print(f"SKIPPED (Missing Info): Email to {recipient or 'N/A'}")
                                continue

                            try:
                                # Ensure selected_sender_email and selected_sender_password are passed
                                success = send_email_message(
                                    sender_email=selected_sender_email,
                                    sender_password=selected_sender_password,
                                    receiver_email=recipient,
                                    subject=subject,
                                    body=body,
                                    attachment_paths=attachment_paths
                                )
                                if success:
                                    status_message = f"{_t('SUCCESS: Email sent to')} {recipient}"
                                    st.session_state.email_sending_status.append(f"🟢 {status_message}")
                                    print(f"SUCCESS: Email sent to {recipient}")
                                else:
                                    status_message = f"{_t('FAILED: Email to')} {recipient}"
                                    st.session_state.email_sending_status.append(f"🔴 {status_message}")
                                    print(f"FAILED: Email to {recipient}")
                                    # Log failed email details to a file
                                    with open(FAILED_EMAILS_LOG_PATH, "a") as f:
                                        f.write(f"{datetime.datetime.now()}: To: {recipient}, Subject: {subject}, Status: Failed\n")

                            except Exception as e:
                                status_message = f"{_t('ERROR sending email to')} {recipient}: {e}"
                                st.session_state.email_sending_status.append(f"🔴 {status_message}")
                                print(f"ERROR sending email to {recipient}: {e}")
                                # Log error details
                                with open(FAILED_EMAILS_LOG_PATH, "a") as f:
                                    f.write(f"{datetime.datetime.now()}: To: {recipient}, Subject: {subject}, Status: Error - {e}\n")

                        st.session_state.sending_in_progress = False
                        st.success(_t("Email sending process completed! Check activity log for details."))
                        st.experimental_rerun() # Refresh to show updated button state and log
                except Exception as ex:
                    st.error(f"{_t('An unexpected error occurred during sending preparation:')} {ex}")
                    st.session_state.email_sending_status.append(f"🔴 {_t('Global Error:')} {ex}")
                    st.session_state.sending_in_progress = False
                    st.experimental_rerun()
                finally:
                    # Clean up temporary directory if it exists
                    if temp_dir and os.path.exists(temp_dir):
                        try:
                            shutil.rmtree(temp_dir)
                            st.session_state.email_sending_status.append(_t("Temporary attachments cleaned up."))
                            print(f"Temporary directory {temp_dir} cleaned up.")
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
                'generic_greeting', 'final_emails_to_send',
                'language' # <--- ADDED THIS LINE FOR THE FIX
            ]:
                if key in st.session_state:
                    del st.session_state[key]
            st.session_state.page = 'generate' # Go back to generate page
            st.experimental_rerun() # Rerun to apply changes and go to new page