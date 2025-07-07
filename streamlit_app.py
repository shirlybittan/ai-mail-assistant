# streamlit_app.py
import streamlit as st
import pandas as pd
import os
import time
import datetime

# Import your custom modules
from data_handler import load_contacts_from_excel
from email_tool import send_email_message, _log_failed_email_to_file
from ai_agent import SmartEmailAgent
from config import LOG_FILE_PATH, FAILED_EMAILS_LOG_PATH, SENDER_EMAIL, SENDER_PASSWORD, OPENAI_API_KEY

# --- Directory Setup (Crucial for consistent paths in Streamlit Cloud) ---
TEMP_DIR = "temp"
if not os.path.exists(TEMP_DIR):
    os.makedirs(TEMP_DIR, exist_ok=True)
    print(f"DEBUG: Created temporary directory: {TEMP_DIR}")

# --- Initialize Session State ---
if 'agent' not in st.session_state:
    st.session_state.agent = SmartEmailAgent()
if 'contacts' not in st.session_state:
    st.session_state.contacts = []
if 'contact_issues' not in st.session_state:
    st.session_state.contact_issues = []
if 'email_subject_preview' not in st.session_state:
    st.session_state.email_subject_preview = ""
if 'email_body_preview' not in st.session_state:
    st.session_state.email_body_preview = ""
if 'log_messages' not in st.session_state:
    st.session_state.log_messages = []
if 'awaiting_confirmation' not in st.session_state:
    st.session_state.awaiting_confirmation = False
if 'user_prompt_for_send' not in st.session_state:
    st.session_state.user_prompt_for_send = ""
if 'personalized_mode_for_send' not in st.session_state:
    st.session_state.personalized_mode_for_send = False
if 'app_just_started' not in st.session_state:
    st.session_state.app_just_started = True

# Initialize prompt_input and personalized_mode if they don't exist
# This ensures that when the app reruns (e.g., after sending emails),
# if these are deleted from session_state, they get their default values back.
if 'prompt_input' not in st.session_state:
    st.session_state.prompt_input = "Generate a friendly welcome email for new subscribers. Introduce our services and offer a special first-time discount code: NEWUSER10."
if 'personalized_mode' not in st.session_state:
    st.session_state.personalized_mode = False


# --- Helper Function for Logging ---
def log_message(message: str, is_error: bool = False):
    timestamp = datetime.datetime.now().strftime("%H:%M:%S")
    log_entry = f"[{timestamp}] {message}"

    if is_error:
        st.session_state.log_messages.append(f"<span style='color:red;'>{log_entry}</span>")
    else:
        st.session_state.log_messages.append(log_entry)

    print(f"CONSOLE LOG: {log_entry}")

    try:
        log_dir = os.path.dirname(LOG_FILE_PATH)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)
            print(f"DEBUG: Created log directory: {log_dir}")

        with open(LOG_FILE_PATH, "a", encoding="utf-8") as f:
            f.write(log_entry + "\n")
    except Exception as e:
        print(f"ERROR: Could not write to main log file '{LOG_FILE_PATH}': {e}")
        st.error(f"Error writing to main log file: {e}")

# --- Streamlit UI Configuration ---
st.set_page_config(
    page_title="Smart Email Messenger AI Agent",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("📧 Smart Email Messenger AI Agent")

if st.session_state.app_just_started:
    log_message(f"Application started. (Current Time: {time.strftime('%Y-%m-%d %H:%M:%S')})")
    log_message(f"Sending log will be saved to: {LOG_FILE_PATH}")
    log_message(f"Failed emails log will be saved to: {FAILED_EMAILS_LOG_PATH}")
    if not SENDER_EMAIL or not SENDER_PASSWORD:
        log_message("WARNING: Email sender credentials (SENDER_EMAIL/SENDER_PASSWORD) are not set. Email sending will likely fail.", is_error=True)
    if not OPENAI_API_KEY:
        log_message("WARNING: OpenAI API Key (OPENAI_API_KEY) is not set. AI features may not work.", is_error=True)
    st.session_state.app_just_started = False

st.sidebar.header("Configuration")

uploaded_file = st.sidebar.file_uploader("Upload Contacts Excel File", type=["xlsx", "xls"])

if uploaded_file is not None:
    temp_file_path = os.path.join(TEMP_DIR, uploaded_file.name)
    with open(temp_file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    log_message(f"Selected file: {uploaded_file.name}")
    
    st.session_state.contacts, st.session_state.contact_issues = load_contacts_from_excel(temp_file_path)
    
    try:
        os.remove(temp_file_path)
        log_message(f"Removed temporary file: {temp_file_path}")
    except OSError as e:
        log_message(f"Error removing temporary file {temp_file_path}: {e}", is_error=True)

    if not st.session_state.contacts:
        st.warning("No valid contacts were loaded from the Excel file. Please check file format and email addresses.")
        log_message("No valid contacts loaded from Excel.", is_error=True)
    else:
        log_message(f"Loaded {len(st.session_state.contacts)} valid contacts from Excel.")
    
    st.sidebar.metric("Valid Contacts", len(st.session_state.contacts))
    st.sidebar.metric("Issues Found", len(st.session_state.contact_issues))
    
    if st.session_state.contact_issues:
        with st.sidebar.expander("Show Contact Loading Issues"):
            for issue in st.session_state.contact_issues:
                st.markdown(f"- <span style='color:orange;'>{issue}</span>", unsafe_allow_html=True)
                log_message(f"  - {issue}", is_error=True)

st.header("Email Generation Settings")

# Note: The `value` for checkbox is now directly from st.session_state.personalized_mode
personalized_checkbox = st.checkbox(
    "Generate personalized email for each contact (uses more AI tokens)",
    value=st.session_state.personalized_mode, # Directly use the session state value
    key="personalized_mode"
)

st.subheader("Email Content Generation Prompt (AI will use this)")
# Note: The `value` for text_area is now directly from st.session_state.prompt_input
user_prompt = st.text_area(
    "Enter your prompt here:",
    value=st.session_state.prompt_input, # Directly use the session state value
    height=150,
    key="prompt_input"
)

if st.button("Generate Preview (for first contact)"):
    if not st.session_state.contacts:
        st.warning("Please upload an Excel file with valid contacts first.")
        log_message("Attempted preview without contacts.", is_error=True)
    elif not user_prompt:
        st.warning("Please enter an email generation prompt.")
        log_message("Attempted preview without prompt.", is_error=True)
    else:
        log_message("Generating email preview for the first contact. This may take a moment...")
        with st.spinner("Generating preview..."):
            try:
                first_contact = st.session_state.contacts[0]
                log_message(f"Using first contact for preview: {first_contact.get('Name', 'Unnamed Contact')}")

                preview_data = st.session_state.agent.generate_email_preview(user_prompt, first_contact)
                
                st.session_state.email_subject_preview = preview_data.get('email_subject', '')
                st.session_state.email_body_preview = preview_data.get('email_body', '')
                raw_llm_output = preview_data.get('raw_llm_output', '')
                
                log_message("Email preview generated successfully.")
                if "LLM did not return valid JSON" in raw_llm_output:
                    log_message(f"Warning: LLM output for preview was not perfectly parsed. Raw output:\n{raw_llm_output}", is_error=True)

            except Exception as e:
                st.error(f"An error occurred during preview generation: {e}")
                log_message(f"Error generating preview: {e}", is_error=True)

st.subheader("Email Preview (for first contact)")
st.text_input("Email Subject:", value=st.session_state.email_subject_preview, key="preview_subject")
st.text_area("Email Body:", value=st.session_state.email_body_preview, height=300, key="preview_body")


# --- Send All Emails Button and Confirmation Flow ---
st.header("5. Send All Emails")

col1_send_btn, col2_send_conf = st.columns([1, 2])

with col1_send_btn:
    if st.button("Send All Emails", key="main_send_button"):
        log_message("MAIN 'Send All Emails' button clicked.")

        if not st.session_state.contacts:
            st.warning("Please upload an Excel file with valid contacts first.")
            log_message("Attempted send without contacts.", is_error=True)
            st.session_state.awaiting_confirmation = False
        else:
            st.session_state.user_prompt_for_send = st.session_state.prompt_input # Use the current input value
            st.session_state.personalized_mode_for_send = st.session_state.personalized_mode # Use the current checkbox value

            email_subject_template = st.session_state.email_subject_preview.strip()
            email_body_template = st.session_state.email_body_preview.strip()
            
            if not st.session_state.personalized_mode_for_send and (not email_subject_template or not email_body_template):
                st.warning("Email subject or body is empty. Please generate or type content for the template.")
                log_message("Attempted send with empty template content.", is_error=True)
                st.session_state.awaiting_confirmation = False
            elif st.session_state.personalized_mode_for_send and not st.session_state.user_prompt_for_send.strip():
                st.warning("Please enter a message generation prompt for personalized emails.")
                log_message("Attempted personalized send without prompt.", is_error=True)
                st.session_state.awaiting_confirmation = False
            else:
                st.session_state.awaiting_confirmation = True
                log_message("Initial send checks passed. Awaiting confirmation...")
                st.rerun()

if st.session_state.awaiting_confirmation:
    with col2_send_conf:
        num_contacts = len(st.session_state.contacts)
        sending_mode = 'FULLY PERSONALIZED (AI generates for each contact)' if st.session_state.personalized_mode_for_send else 'TEMPLATE (AI generated preview, sent to all)'
        
        st.info(
            f"You are about to send emails to **{num_contacts} contacts**.\n"
            f"Sending Mode: **{sending_mode}**\n\n"
            "Are you sure you want to proceed?"
        )
        
        if st.button("Confirm Send All Emails", key="confirm_send_final_button"):
            log_message("CONFIRM 'Confirm Send All Emails' button clicked. Initiating sending process...")
            
            st.session_state.awaiting_confirmation = False
            
            if not st.session_state.contacts:
                log_message("Error: No contacts found at time of sending. Skipping send.", is_error=True)
                st.error("No contacts found. Please re-upload your file.")
            else:
                total_success = 0
                total_failed = 0
                
                with st.spinner("Sending emails... Please do not close this tab."):
                    progress_text_placeholder = st.empty()
                    
                    for i, contact in enumerate(st.session_state.contacts):
                        current_user_prompt = st.session_state.user_prompt_for_send
                        is_personalized = st.session_state.personalized_mode_for_send

                        contact_name = contact.get("Name", f"Contact {i+1}")
                        contact_email = contact.get("Email", '').strip()
                        
                        progress_text_placeholder.text(f"Sending to {contact_name} ({i+1}/{num_contacts})...")

                        if not contact_email or "@" not in contact_email:
                            log_message(f"Skipping contact {contact_name} due to invalid/missing email: {contact_email}", is_error=True)
                            st.warning(f"Skipping {contact_name}: Invalid email format.")
                            total_failed += 1
                            _log_failed_email_to_file(contact_email, "(N/A)", "(N/A)", f"Invalid/missing email format: {contact_email}")
                            continue

                        email_subject = st.session_state.email_subject_preview
                        email_body = st.session_state.email_body_preview

                        if is_personalized:
                            log_message(f"Generating personalized email for {contact_name}...")
                            try:
                                personalized_data = st.session_state.agent.generate_email_preview(current_user_prompt, contact)
                                email_subject = personalized_data.get('email_subject', email_subject)
                                email_body = personalized_data.get('email_body', email_body)
                                
                                if personalized_data.get('raw_llm_output') and "LLM did not return valid JSON" in personalized_data['raw_llm_output']:
                                    log_message(f"Warning: LLM output for {contact_name} was not perfectly parsed.", is_error=True)
                                log_message(f"Personalized email generated for {contact_name}.")
                            except Exception as e:
                                log_message(f"Error generating personalized email for {contact_name}: {e}. Using template fallback.", is_error=True)
                                st.error(f"Failed to personalize for {contact_name}. See logs.")
                                total_failed += 1
                                _log_failed_email_to_file(contact_email, email_subject, email_body, f"AI personalization failed: {e}")
                                continue
                        
                        log_message(f"Attempting to send email to {contact_name} ({contact_email})...")
                        email_result = send_email_message(to_email=contact_email, subject=email_subject, body=email_body)

                        if email_result["status"] == "success":
                            total_success += 1
                            log_message(f"Email sent successfully to {contact_name}.", is_error=False)
                        else:
                            total_failed += 1
                            log_message(f"Failed to send email to {contact_name}: {email_result['message']}", is_error=True)
                                
                progress_text_placeholder.empty()

                st.subheader("--- Sending Complete ---")
                st.success(f"Successfully sent {total_success} emails.")
                if total_failed > 0:
                    st.error(f"Failed or Skipped {total_failed} emails. Check the Activity Log and 'failed_emails_log.txt' for details.")
                else:
                    st.info("All emails sent successfully!")

                log_message(f"\n--- Sending Complete ---")
                log_message(f"Total contacts processed: {num_contacts}")
                log_message(f"Successful emails sent: {total_success}")
                log_message(f"Failed or Skipped emails: {total_failed}")
                
                # --- Crucial Reset Logic for Widget-Bound Session State ---
                # To reset widgets, it's safer to delete the keys from session_state
                # so that on the next rerun, they get re-initialized by the `if not in st.session_state` blocks.
                if 'email_subject_preview' in st.session_state:
                    del st.session_state.email_subject_preview
                if 'email_body_preview' in st.session_state:
                    del st.session_state.email_body_preview
                if 'contacts' in st.session_state:
                    del st.session_state.contacts
                
                # These are the ones causing the issue:
                if 'prompt_input' in st.session_state:
                    del st.session_state.prompt_input # This will cause the text_area to reset
                if 'user_prompt_for_send' in st.session_state:
                    del st.session_state.user_prompt_for_send
                if 'personalized_mode' in st.session_state:
                    del st.session_state.personalized_mode # This will cause the checkbox to reset
                if 'personalized_mode_for_send' in st.session_state:
                    del st.session_state.personalized_mode_for_send
                
                # Clear logs displayed in the UI for a fresh start
                st.session_state.log_messages = [] 
                
                st.success("Email sending process completed and UI reset.")
                st.rerun() # Trigger a full rerun to apply the reset state


# --- Activity Log Display ---
st.subheader("Activity Log")
if st.session_state.log_messages:
    for msg in reversed(st.session_state.log_messages):
        st.markdown(msg, unsafe_allow_html=True)
else:
    st.info("No activity logs yet. Actions will appear here.")