# streamlit_app.py
import streamlit as st
import pandas as pd
import os
import time
import datetime

# Import your custom modules
from data_handler import load_contacts_from_excel
from email_tool import send_email_message
from ai_agent import SmartEmailAgent
from config import LOG_FILE_PATH, FAILED_EMAILS_LOG_PATH # Import log paths from config

# --- Initialize Session State ---
# This is crucial for maintaining data across Streamlit reruns
if 'agent' not in st.session_state:
    st.session_state.agent = SmartEmailAgent() # Initialize AI agent once
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

# --- Helper Function for Logging (to mimic your GUI's log) ---
def log_message(message, is_error=False):
    timestamp = datetime.datetime.now().strftime("%H:%M:%S")
    log_entry = f"[{timestamp}] {message}"
    if is_error:
        # For Streamlit, we can use st.error or st.warning for visual cues
        st.session_state.log_messages.append(f"<span style='color:red;'>{log_entry}</span>")
    else:
        st.session_state.log_messages.append(log_entry)

    # Also write to file for persistence
    try:
        with open(LOG_FILE_PATH, "a", encoding="utf-8") as f:
            f.write(log_entry + "\n")
    except Exception as e:
        st.error(f"Error writing to main log file: {e}")

# --- Streamlit UI ---
st.set_page_config(
    page_title="Smart Email Messenger AI Agent",
    layout="wide", # Use wide layout for more space
    initial_sidebar_state="expanded"
)

st.title("📧 Smart Email Messenger AI Agent")

# Initial Log Messages
if not st.session_state.log_messages: # Only add these once on first run
    log_message(f"Application started. (Current Time: {time.strftime('%Y-%m-%d %H:%M:%S')})")
    log_message(f"Sending log saved to: {LOG_FILE_PATH}")
    log_message(f"Failed emails log saved to: {FAILED_EMAILS_LOG_PATH}")

st.sidebar.header("Configuration")

# File Upload
uploaded_file = st.sidebar.file_uploader("Upload Contacts Excel File", type=["xlsx", "xls"])

if uploaded_file is not None:
    # Save the uploaded file temporarily to process it
    temp_file_path = os.path.join("temp", uploaded_file.name)
    os.makedirs("temp", exist_ok=True)
    with open(temp_file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    log_message(f"Selected file: {uploaded_file.name}")
    
    # Load contacts
    st.session_state.contacts, st.session_state.contact_issues = load_contacts_from_excel(temp_file_path)
    
    # Clean up temporary file (optional, or keep for debugging)
    # os.remove(temp_file_path)

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

# Main content area
st.header("Email Generation Settings")

# Personalization checkbox
personalized_checkbox = st.checkbox(
    "Generate personalized email for each contact (uses more AI tokens)",
    value=False,
    key="personalized_mode"
)

# Prompt Input
st.subheader("Email Content Generation Prompt (AI will use this)")
user_prompt = st.text_area(
    "Enter your prompt here:",
    "Generate a friendly welcome email for new subscribers. Introduce our services and offer a special first-time discount code: NEWUSER10.",
    height=150,
    key="prompt_input"
)

# Preview Button
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
                log_message(f"Using first contact for preview: {first_contact.get('name', 'Unnamed Contact')}")
                
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

# Preview Area
st.subheader("Email Preview (for first contact)")
st.text_input("Email Subject:", value=st.session_state.email_subject_preview, key="preview_subject")
st.text_area("Email Body:", value=st.session_state.email_body_preview, height=300, key="preview_body")


# Send Emails Button
if st.button("Send All Emails"):
    if not st.session_state.contacts:
        st.warning("Please upload an Excel file with valid contacts first.")
        log_message("Attempted send without contacts.", is_error=True)
        st.stop() # Stop execution until contacts are loaded

    is_personalized = st.session_state.personalized_mode # Get current value from session state
    
    email_subject_template = st.session_state.preview_subject.strip()
    email_body_template = st.session_state.preview_body.strip()

    if not is_personalized and (not email_subject_template or not email_body_template):
        st.warning("Email subject or body is empty. Please generate or type content for the template.")
        log_message("Attempted send with empty template content.", is_error=True)
        st.stop()

    if is_personalized and not user_prompt.strip():
        st.warning("Please enter a message generation prompt for personalized emails.")
        log_message("Attempted personalized send without prompt.", is_error=True)
        st.stop()


    num_contacts = len(st.session_state.contacts)
    confirmation_message = (
        f"You are about to send emails to {num_contacts} contacts.\n"
        f"Sending Mode: {'FULLY PERSONALIZED (AI generates for each contact)' if is_personalized else 'TEMPLATE (AI generated preview, sent to all)'}\n\n"
        "Are you sure you want to proceed?"
    )

    if st.checkbox("Confirm to Send?", key="confirm_send_checkbox"): # Simple confirmation
        log_message("Email sending process initiated...")
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        total_success = 0
        total_failed = 0

        for i, contact in enumerate(st.session_state.contacts):
            current_contact_name = contact.get('name', 'Unnamed Contact')
            current_email = contact.get('email', '').strip()

            log_message(f"\n--- [{i+1}/{num_contacts}] Processing contact: {current_contact_name} ({current_email}) ---")
            status_text.text(f"Processing {current_contact_name} ({i+1}/{num_contacts})...")
            progress_bar.progress((i + 1) / num_contacts)
            
            final_email_subject = ""
            final_email_body = ""

            if is_personalized:
                log_message(f"  Generating personalized email for {current_contact_name}...")
                try:
                    ai_gen_result = st.session_state.agent.generate_email_preview(user_prompt, contact)
                    final_email_subject = ai_gen_result.get("email_subject", "")
                    final_email_body = ai_gen_result.get("email_body", "")
                    if ai_gen_result.get('raw_llm_output') and "LLM did not return valid JSON" in ai_gen_result['raw_llm_output']:
                         log_message(f"    AI generation issue for {current_contact_name}: {ai_gen_result['raw_llm_output']}", is_error=True)
                         if not final_email_subject:
                             final_email_subject = "(AI Generation Failed) " + email_subject_template
                         if not final_email_body:
                             final_email_body = "(AI Generation Failed) " + email_body_template
                except Exception as e:
                    log_message(f"    AI generation FAILED for {current_contact_name}: {e}. Using template fallback.", is_error=True)
                    final_email_subject = "(AI Generation Failed) " + email_subject_template
                    final_email_body = "(AI Generation Failed) " + email_body_template
            else:
                final_email_subject = email_subject_template
                final_email_body = email_body_template

            if current_email:
                log_message(f"  Attempting Email for {current_contact_name}...")
                email_result = send_email_message(current_email, final_email_subject, final_email_body)
                log_message(f"    - Email: {email_result['status']} - {email_result['message']}",
                            is_error=(email_result['status'] == 'error'))
                
                if email_result['status'] == 'success':
                    total_success += 1
                else:
                    total_failed += 1
            else:
                total_failed += 1
                log_message(f"    - Skipped: No email address for {current_contact_name}.", is_error=True)

            time.sleep(0.05) # Small delay to prevent API rate limits

        st.subheader("--- Sending Complete ---")
        st.success(f"Successfully sent {total_success} emails.")
        st.error(f"Failed or Skipped {total_failed} emails.")
        st.info("Check the Activity Log and 'failed_emails_log.txt' for details.")
        log_message(f"\n--- Sending Complete ---")
        log_message(f"Total contacts processed: {num_contacts}")
        log_message(f"Successful emails sent: {total_success}")
        log_message(f"Failed or Skipped emails: {total_failed}")
        status_text.empty() # Clear status text
        progress_bar.empty() # Clear progress bar

        # Reset confirm checkbox after sending is done
        st.session_state.confirm_send_checkbox = False # This might require a rerun or direct button press for visual reset


# --- Activity Log Display ---
st.subheader("Activity Log")
# Display logs with markdown for colors
for msg in st.session_state.log_messages:
    st.markdown(msg, unsafe_allow_html=True)