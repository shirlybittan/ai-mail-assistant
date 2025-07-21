# streamlit_app.py

import streamlit as st
import pandas as pd
from data_handler import load_contacts_from_excel
from email_generator import SmartEmailAgent
from email_tool import send_email_message
from config import SENDER_CREDENTIALS, OPENAI_API_KEY # Ensure SENDER_CREDENTIALS is imported
import tempfile # For creating temporary files/directories
import os       # For path operations
import shutil   # For deleting temporary directories
import datetime # For timestamping in logs

# Set Streamlit page configuration
st.set_page_config(layout="wide", page_title="AI Email Assistant")

# --- Initialize session state variables ---
# Ensure ALL session state variables are initialized here
if 'generated_emails' not in st.session_state:
    st.session_state.generated_emails = []
if 'email_sending_status' not in st.session_state:
    st.session_state.email_sending_status = []
if 'show_preview' not in st.session_state:
    st.session_state.show_preview = False
if 'sender_email_choice' not in st.session_state:
    st.session_state.sender_email_choice = None
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
    st.session_state.personalize_emails = True


st.title("📧 AI Email Assistant")

# --- Configuration and User Input ---
st.header("Configuration")

# Check if sender credentials are loaded from secrets
if not SENDER_CREDENTIALS:
    st.error("Email sender credentials not found in Streamlit Secrets. Please configure them correctly.")
    st.stop() # Stop execution if no sender credentials are set

# Extract available sender emails for the selectbox
available_sender_emails = list(SENDER_CREDENTIALS.keys())
if not available_sender_emails:
    st.error("No sender email addresses configured in secrets. Please add at least one email under [SENDER_CREDENTIALS].")
    st.stop()

# Dropdown for sender email selection
st.session_state.sender_email_choice = st.selectbox(
    "Choose Sender Email:",
    available_sender_emails,
    index=0 if available_sender_emails else None # Default to the first email in the list
)

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
        "png", "jpg", "jpeg", "gif",  # Image formats
        "mp4", "mov", "avi",          # Video formats
        "pdf",                        # PDF documents
        "doc", "docx",                # Word documents
        "xls", "xlsx",                # Excel documents
        "ppt", "pptx",                # PowerPoint presentations
        "txt", "csv", "rtf"           # Text and rich text formats
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
        st.error("OpenAI API Key not found in Streamlit Secrets. Cannot generate emails.")
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
        
        generation_progress_bar.empty() # Remove progress bar after completion
        st.success(f"Generated {len(st.session_state.generated_emails)} emails!")
        st.session_state.show_preview = True # Show preview by default after generation

# --- Email Sending Logic ---
st.header("Send Emails")

if st.session_state.generated_emails:
    col1, col2 = st.columns([1, 1])

    with col1:
        st.write(f"You are about to send emails to **{len(st.session_state.generated_emails)} contacts**.")
        st.write(f"**Sending Mode:** {'FULLY PERSONALIZED' if st.session_state.personalize_emails else 'TEMPLATE-BASED'}")

        # Retrieve the selected sender email and its corresponding password
        selected_sender_email = st.session_state.sender_email_choice
        selected_sender_password = SENDER_CREDENTIALS.get(selected_sender_email)

        if not selected_sender_password:
            st.error(f"Error: Password not found for selected sender email: `{selected_sender_email}`. Please check your Streamlit Secrets.")
        else:
            if st.button("Confirm Send All Emails", key="confirm_send_button"):
                st.write("--- Sending Emails ---")
                success_count = 0
                failed_or_skipped_count = 0
                st.session_state.email_sending_status = [] # Clear previous status

                send_progress_bar = st.progress(0, text="Sending emails...")

                # --- Attachment Handling: Save uploaded files to a temporary directory ---
                temp_dir = None # Initialize to None
                attachment_paths = []

                if st.session_state.uploaded_attachments:
                    try:
                        temp_dir = tempfile.mkdtemp() # Create a unique temporary directory
                        st.session_state.email_sending_status.append(f"Preparing {len(st.session_state.uploaded_attachments)} attachment(s)...")

                        for uploaded_file in st.session_state.uploaded_attachments:
                            file_path = os.path.join(temp_dir, uploaded_file.name)
                            with open(file_path, "wb") as f:
                                f.write(uploaded_file.getbuffer()) # Write the file content to the temp path
                            attachment_paths.append(file_path)
                        st.session_state.email_sending_status.append("Attachments prepared.")
                        print(f"CONSOLE LOG: streamlit_app.py: Attachments saved to temporary directory: {temp_dir}")
                    except Exception as e:
                        st.session_state.email_sending_status.append(f"ERROR: Could not prepare attachments: {e}")
                        st.error(f"Could not prepare attachments: {e}. Email sending aborted.")
                        send_progress_bar.empty()
                        # Clean up temp_dir if it was created before stopping
                        if temp_dir and os.path.exists(temp_dir):
                            try: shutil.rmtree(temp_dir)
                            except Exception as cleanup_e: print(f"Cleanup error: {cleanup_e}")
                        st.stop() # Stop sending if attachment prep fails

                # --- END Attachment Handling ---

                try: # This try block wraps the entire sending loop to ensure cleanup
                    for i, email_data in enumerate(st.session_state.generated_emails):
                        st.session_state.email_sending_status.append(f"Attempting to send email to {email_data['name']} ({email_data['email']})...")
                        # Display only the last few status updates
                        st.empty().write("\n".join(st.session_state.email_sending_status[-5:]))

                        result = send_email_message(
                            sender_email=selected_sender_email,
                            sender_password=selected_sender_password,
                            to_email=email_data['email'],
                            subject=email_data['subject'],
                            body=email_data['body'],
                            attachments=attachment_paths # Pass the list of attachment file paths
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

                finally: # Ensures cleanup even if an error occurs during sending
                    send_progress_bar.empty() # Remove progress bar after completion
                    if temp_dir and os.path.exists(temp_dir):
                        try:
                            shutil.rmtree(temp_dir) # Delete the temporary directory and its contents
                            st.session_state.email_sending_status.append("Temporary attachments cleaned up.")
                            print(f"CONSOLE LOG: streamlit_app.py: Cleaned up temporary directory: {temp_dir}")
                        except Exception as cleanup_e:
                            st.session_state.email_sending_status.append(f"ERROR: Could not clean up temporary attachments: {cleanup_e}")
                            print(f"ERROR: streamlit_app.py: Could not clean up temporary directory {temp_dir}: {cleanup_e}")

                st.markdown("---")
                st.subheader("Activity Log")
                for log_entry in reversed(st.session_state.email_sending_status):
                    st.write(log_entry)
                
                # Reset UI state to start a new session
                if st.button("Start New Email Session"):
                    for key in st.session_state.keys():
                        del st.session_state[key]
                    st.rerun()

    with col2:
        if st.session_state.show_preview and st.session_state.generated_emails:
            st.subheader("Preview Email Content")
            st.warning("This is a preview of the FIRST email generated. The content will vary if 'Personalize Emails' is checked.")
            preview_email = st.session_state.generated_emails[0]
            st.markdown(f"**From:** `{selected_sender_email}`") # Display chosen sender email
            st.markdown(f"**To:** `{preview_email['name']} <{preview_email['email']}>`")
            st.markdown(f"**Subject:** `{preview_email['subject']}`")
            st.markdown("---")
            st.markdown(preview_email['body'])
            st.markdown("---")

else:
    st.info("Upload an Excel file and generate emails to see the sending options.")