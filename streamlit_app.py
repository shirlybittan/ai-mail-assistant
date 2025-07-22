# streamlit_app.py

import streamlit as st
import pandas as pd
from data_handler import load_contacts_from_excel
from email_generator import SmartEmailAgent
from email_tool import send_email_message
# Import individual variables, not a dict from config
from config import SENDER_CREDENTIALS, OPENAI_API_KEY, SENDER_EMAIL, SENDER_PASSWORD # Added SENDER_EMAIL, SENDER_PASSWORD
import tempfile
import os
import shutil
import datetime

# Set Streamlit page configuration
st.set_page_config(layout="wide", page_title="AI Email Assistant")

# --- DEBUGGING INFO START ---
#st.subheader("Debugging Info (REMOVE AFTER TROUBLESHOOTING)")
#st.write("All secrets from st.secrets:", st.secrets.to_dict()) # This will show the new consolidated structure
#st.write("Sender credentials (from config):", SENDER_CREDENTIALS)
#st.write("OpenAI key (from config):", OPENAI_API_KEY)
#st.write("DEBUG: SENDER_EMAIL:", SENDER_EMAIL) # Added for specific check
#st.write("DEBUG: SENDER_PASSWORD present:", bool(SENDER_PASSWORD)) # Added for specific check
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


st.title("📧 AI Email Assistant")

# --- Configuration and User Input ---
st.header("Configuration")

# Check if sender credentials are loaded from config.py
# Use the individual SENDER_EMAIL and SENDER_PASSWORD for checks
if not SENDER_EMAIL or not SENDER_PASSWORD:
    st.error("Sender email or password not found. Please configure them correctly in Streamlit Secrets under [app_credentials].")
    st.stop()
if not OPENAI_API_KEY:
    st.error("OpenAI API Key not found. Please configure it correctly in Streamlit Secrets under [app_credentials].")
    st.stop()

# Display the single sender email instead of a selectbox
st.info(f"Using sender email: **{SENDER_EMAIL}**")
selected_sender_email = SENDER_EMAIL # Set the selected email directly


# File uploader for contacts list
uploaded_file = st.file_uploader("Upload your contacts Excel file", type=["xlsx", "xls"])

if uploaded_file is not None:
    st.session_state.contacts, st.session_state.contact_issues = load_contacts_from_excel(uploaded_file)
    if st.session_state.contacts:
        st.success(f"Loaded {len(st.session_state.contacts)} contacts.")
    if st.session_state.contact_issues:
        st.warning("Some contacts had issues:")
        for issue in st.session_state.contact_issues:
            st.write(f"- {issue}")
else:
    st.info("Please upload an Excel file to proceed.")
    st.session_state.contacts = [] # Clear contacts if file is removed

# Add attachments
st.subheader("Add Attachments (Optional)")
st.session_state.uploaded_attachments = st.file_uploader(
    "Upload photos, videos, or documents (recommended total size < 25MB per mail)",
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
    st.info(f"{len(st.session_state.uploaded_attachments)} file(s) selected for attachment.")

# User input for email generation
st.subheader("Email Content Request")
st.session_state.user_prompt = st.text_area(
    "Describe the email you want to send:",
    value=st.session_state.user_prompt,
    placeholder="e.g., 'An invitation to our annual charity gala, highlighting guest speaker Jane Doe and live music.'",
    height=100
)
st.session_state.user_email_context = st.text_area(
    "Optional: Provide context about your email style or content preferences (e.g., 'I prefer concise, direct language and a friendly tone.'):",
    value=st.session_state.user_email_context,
    placeholder="e.g., 'I prefer formal language and clear calls to action.'",
    height=80
)
st.session_state.personalize_emails = st.checkbox(
    "Personalize each email (uses contact name and makes it unique)",
    value=st.session_state.personalize_emails
)

# --- Email Generation ---
st.header("Generate Emails")

if st.button("Generate Emails for Contacts"):
    if not st.session_state.contacts:
        st.error("Please upload an Excel file with contacts first.")
    elif not st.session_state.user_prompt:
        st.error("Please provide a description for the email.")
    elif not OPENAI_API_KEY:
        st.error("OpenAI API Key not found. Cannot generate emails.")
    else:
        st.session_state.generated_emails = [] # Clear previous generation
        
        # Initialize the AI agent
        try:
            agent = SmartEmailAgent(openai_api_key=OPENAI_API_KEY)
        except ValueError as e:
            st.error(f"Error initializing AI agent: {e}. Please check your OpenAI API Key.")
            st.stop()

        generation_progress_bar = st.progress(0, text="Generating emails...")
        for i, contact in enumerate(st.session_state.contacts):
            email_output = agent.generate_email(
                prompt=st.session_state.user_prompt,
                contact_name=contact['name'],
                personalize=st.session_state.personalize_emails,
                user_email_context=st.session_state.user_email_context
            )
            st.session_state.generated_emails.append({
                "name": contact['name'],
                "email": contact['email'],
                "subject": email_output['subject'],
                "body": email_output['body']
            })
            generation_progress_bar.progress((i + 1) / len(st.session_state.contacts), text=f"Generating email for {contact['name']}...")
        
        generation_progress_bar.empty()
        st.success(f"Generated {len(st.session_state.generated_emails)} emails!")
        st.session_state.show_preview = True

# --- Email Sending Logic ---
st.header("Send Emails")

if st.session_state.generated_emails:
    col1, col2 = st.columns([1, 1])

    with col1:
        st.write(f"You are about to send emails to **{len(st.session_state.generated_emails)} contacts**.")
        st.write(f"**Sending Mode:** {'FULLY PERSONALIZED' if st.session_state.personalize_emails else 'TEMPLATE-BASED'}")

        # Use the SENDER_PASSWORD directly from config
        selected_sender_password = SENDER_PASSWORD # Changed to direct variable

        if not selected_sender_password:
            st.error(f"Error: Password not found for sender email: `{SENDER_EMAIL}`. Please check your Streamlit Secrets.")
        else:
            if st.button("Confirm Send All Emails", key="confirm_send_button"):
                st.write("--- Sending Emails ---")
                success_count = 0
                failed_or_skipped_count = 0
                st.session_state.email_sending_status = []

                send_progress_bar = st.progress(0, text="Sending emails...")

                temp_dir = None
                attachment_paths = []

                if st.session_state.uploaded_attachments:
                    try:
                        temp_dir = tempfile.mkdtemp()
                        st.session_state.email_sending_status.append(f"Preparing {len(st.session_state.uploaded_attachments)} attachment(s)...")

                        for uploaded_file in st.session_state.uploaded_attachments:
                            file_path = os.path.join(temp_dir, uploaded_file.name)
                            with open(file_path, "wb") as f:
                                f.write(uploaded_file.getbuffer())
                            attachment_paths.append(file_path)
                        st.session_state.email_sending_status.append("Attachments prepared.")
                        print(f"CONSOLE LOG: streamlit_app.py: Attachments saved to temporary directory: {temp_dir}")
                    except Exception as e:
                        st.session_state.email_sending_status.append(f"ERROR: Could not prepare attachments: {e}")
                        st.error(f"Could not prepare attachments: {e}. Email sending aborted.")
                        send_progress_bar.empty()
                        if temp_dir and os.path.exists(temp_dir):
                            try: shutil.rmtree(temp_dir)
                            except Exception as cleanup_e: print(f"Cleanup error: {cleanup_e}")
                        st.stop()

                try:
                    for i, email_data in enumerate(st.session_state.generated_emails):
                        st.session_state.email_sending_status.append(f"Attempting to send email to {email_data['name']} ({email_data['email']})...")
                        st.empty().write("\n".join(st.session_state.email_sending_status[-5:]))

                        result = send_email_message(
                            sender_email=selected_sender_email,
                            sender_password=selected_sender_password,
                            to_email=email_data['email'],
                            subject=email_data['subject'],
                            body=email_data['body'],
                            attachments=attachment_paths
                        )

                        if result["status"] == "success":
                            st.session_state.email_sending_status.append(f"Email sent successfully to {email_data['name']}.")
                            success_count += 1
                        else:
                            st.session_state.email_sending_status.append(f"Failed to send email to {email_data['name']}: {result['message']}")
                            failed_or_skipped_count += 1

                        send_progress_bar.progress((i + 1) / len(st.session_state.generated_emails))

                    st.session_state.email_sending_status.append("--- Sending Complete ---")
                    st.success("All emails processed!")
                    st.session_state.email_sending_status.append(f"Total contacts processed: {len(st.session_state.generated_emails)}")
                    st.session_state.email_sending_status.append(f"Successful emails sent: {success_count}")
                    st.session_state.email_sending_status.append(f"Failed or Skipped emails: {failed_or_skipped_count}")

                finally:
                    send_progress_bar.empty()
                    if temp_dir and os.path.exists(temp_dir):
                        try:
                            shutil.rmtree(temp_dir)
                            st.session_state.email_sending_status.append("Temporary attachments cleaned up.")
                            print(f"CONSOLE LOG: streamlit_app.py: Cleaned up temporary directory: {temp_dir}")
                        except Exception as cleanup_e:
                            st.session_state.email_sending_status.append(f"ERROR: Could not clean up temporary attachments: {cleanup_e}")
                            print(f"ERROR: streamlit_app.py: Could not clean up temporary directory {temp_dir}: {cleanup_e}")

                st.markdown("---")
                st.subheader("Activity Log")
                for log_entry in reversed(st.session_state.email_sending_status):
                    st.write(log_entry)
                
                if st.button("Start New Email Session"):
                    for key in st.session_state.keys():
                        del st.session_state[key]
                    st.rerun()

    with col2:
        if st.session_state.show_preview and st.session_state.generated_emails:
            st.subheader("Preview Email Content")
            st.warning("This is a preview of the FIRST email generated. The content will vary if 'Personalize Emails' is checked.")
            preview_email = st.session_state.generated_emails[0]
            st.markdown(f"**From:** `{selected_sender_email}`")
            st.markdown(f"**To:** `{preview_email['name']} <{preview_email['email']}>`")
            st.markdown(f"**Subject:** `{preview_email['subject']}`")
            st.markdown("---")
            st.markdown(preview_email['body'])
            st.markdown("---")

else:
    st.info("Upload an Excel file and generate emails to see the sending options.")