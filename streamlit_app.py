# streamlit_app.py (Relevant sections)
import streamlit as st
import pandas as pd
from data_handler import load_contacts_from_excel
from email_generator import SmartEmailAgent
from email_tool import send_email_message 
from config import SENDER_CREDENTIALS, OPENAI_API_KEY # Import the new SENDER_CREDENTIALS

# Initialize session state variables
# ... (Keep existing initialization, including 'sender_email_choice') ...

# --- Configuration and User Input ---
st.header("Configuration")

# Check if sender credentials are loaded from secrets
if not SENDER_CREDENTIALS:
    st.error("Email sender credentials not found in Streamlit Secrets. Please configure them.")
    st.stop() # Stop execution if no sender credentials are set

# Extract available sender emails for the selectbox
available_sender_emails = list(SENDER_CREDENTIALS.keys())
if not available_sender_emails:
    st.error("No sender email addresses configured in secrets.toml under [SENDER_CREDENTIALS].")
    st.stop()

# Dropdown for sender email selection
st.session_state.sender_email_choice = st.selectbox(
    "Choose Sender Email:",
    available_sender_emails,
    index=0 # Default to the first email in the list
)

# ... (Keep your existing user prompt and personalization checkbox inputs) ...


# --- Email Generation ---
# ... (Keep your existing email generation logic using SmartEmailAgent) ...


# --- Email Sending Logic ---
st.header("Send Emails")
if st.session_state.generated_emails:
    st.session_state.show_preview = True # Ensure preview is shown if emails are generated

    col1, col2 = st.columns([1, 1])

    with col1:
        st.write(f"You are about to send emails to **{len(st.session_state.generated_emails)} contacts**.")
        st.write(f"**Sending Mode:** {'FULLY PERSONALIZED' if personalize_emails else 'TEMPLATE-BASED'}")

        # Retrieve the selected sender email and its corresponding password
        selected_sender_email = st.session_state.sender_email_choice
        selected_sender_password = SENDER_CREDENTIALS.get(selected_sender_email)

        if not selected_sender_password:
            st.error(f"Error: Password not found for selected sender email: {selected_sender_email}. Please check your Streamlit Secrets.")
        else:
            if st.button("Confirm Send All Emails", key="confirm_send_button"):
                st.write("--- Sending Complete ---")
                success_count = 0
                failed_or_skipped_count = 0
                st.session_state.email_sending_status = [] # Clear previous status

                send_progress_bar = st.progress(0, text="Sending emails...")

                for i, email_data in enumerate(st.session_state.generated_emails):
                    st.session_state.email_sending_status.append(f"Attempting to send email to {email_data['name']} ({email_data['email']})...")
                    st.empty().write("\n".join(st.session_state.email_sending_status[-5:])) # Show last 5 status updates

                    # Call the send_email_message with the dynamically chosen sender email and password
                    result = send_email_message(
                        sender_email=selected_sender_email, # Pass sender email
                        sender_password=selected_sender_password, # Pass sender password
                        to_email=email_data['email'],
                        subject=email_data['subject'],
                        body=email_data['body']
                    )

                    if result["status"] == "success":
                        st.session_state.email_sending_status.append(f"Email sent successfully to {email_data['name']}.")
                        success_count += 1
                    else:
                        st.session_state.email_sending_status.append(f"Failed to send email to {email_data['name']}: {result['message']}")
                        failed_or_skipped_count += 1

                    send_progress_bar.progress((i + 1) / len(st.session_state.generated_emails))

                st.session_state.email_sending_status.append("--- Sending Complete ---")
                st.success("All emails sent successfully!")
                st.session_state.email_sending_status.append(f"Total contacts processed: {len(st.session_state.generated_emails)}")
                st.session_state.email_sending_status.append(f"Successful emails sent: {success_count}")
                st.session_state.email_sending_status.append(f"Failed or Skipped emails: {failed_or_skipped_count}")

                st.markdown("---")
                st.subheader("Activity Log")
                # Removed 'datetime' import dependency for cleaner code presentation
                # If you need timestamping, ensure 'import datetime' is at the top of your streamlit_app.py
                for log_entry in reversed(st.session_state.email_sending_status):
                    st.write(log_entry)

                send_progress_bar.empty() # Remove progress bar after completion

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