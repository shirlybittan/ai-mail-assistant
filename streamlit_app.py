# streamlit_app.py
import streamlit as st
import pandas as pd
import os
import time
import datetime

# Import your custom modules
from data_handler import load_contacts_from_excel
from email_tool import send_email_message, _log_failed_email_to_file # Added _log_failed_email_to_file for direct use in app
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
if 'awaiting_confirmation' not in st.session_state: # New flag for 2-step send confirmation
    st.session_state.awaiting_confirmation = False
if 'user_prompt_for_send' not in st.session_state: # Store prompt when send is initiated
    st.session_state.user_prompt_for_send = ""
if 'personalized_mode_for_send' not in st.session_state: # Store personalized mode when send is initiated
    st.session_state.personalized_mode_for_send = False

# --- Helper Function for Logging ---
def log_message(message: str, is_error: bool = False):
    timestamp = datetime.datetime.now().strftime("%H:%M:%S")
    log_entry = f"[{timestamp}] {message}"

    # Append to session state for in-app display
    if is_error:
        st.session_state.log_messages.append(f"<span style='color:red;'>{log_entry}</span>")
    else:
        st.session_state.log_messages.append(log_entry)

    # Also print to console/Streamlit Cloud logs for persistent debugging
    print(log_entry)

    # Also write to file for persistent log file
    try:
        with open(LOG_FILE_PATH, "a", encoding="utf-8") as f:
            f.write(log_entry + "\n")
    except Exception as e:
        # If log file itself fails, print to console and show error in app
        print(f"Error writing to main log file: {e}")
        st.error(f"Error writing to main log file: {e}")

# --- Streamlit UI ---
st.set_page_config(
    page_title="Smart Email Messenger AI Agent",
    layout="wide", # Use wide layout for more space
    initial_sidebar_state="expanded"
)

st.title("📧 Smart Email Messenger AI Agent")

# Initial Log Messages (only add these once on first run or clear)
if not st.session_state.log_messages:
    log_message(f"Application started. (Current Time: {time.strftime('%Y-%m-%d %H:%M:%S')})")
    log_message(f"Sending log saved to: {LOG_FILE_PATH}")
    log_message(f"Failed emails log saved to: {FAILED_EMAILS_LOG_PATH}")

st.sidebar.header("Configuration")

# File Upload
uploaded_file = st.sidebar.file_uploader("Upload Contacts Excel File", type=["xlsx", "xls"])

if uploaded_file is not None:
    # Ensure 'temp' directory exists
    os.makedirs("temp", exist_ok=True)
    temp_file_path = os.path.join("temp", uploaded_file.name)
    with open(temp_file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    log_message(f"Selected file: {uploaded_file.name}")
    
    # Load contacts
    st.session_state.contacts, st.session_state.contact_issues = load_contacts_from_excel(temp_file_path)
    
    # Clean up temporary file
    try:
        os.remove(temp_file_path)
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

# Main content area
st.header("Email Generation Settings")

# Personalization checkbox
personalized_checkbox = st.checkbox(
    "Generate personalized email for each contact (uses more AI tokens)",
    value=st.session_state.get('personalized_mode', False), # Retain state
    key="personalized_mode"
)

# Prompt Input
st.subheader("Email Content Generation Prompt (AI will use this)")
user_prompt = st.text_area(
    "Enter your prompt here:",
    value=st.session_state.get('prompt_input', "Generate a friendly welcome email for new subscribers. Introduce our services and offer a special first-time discount code: NEWUSER10."),
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
                log_message(f"Using first contact for preview: {first_contact.get('Name', 'Unnamed Contact')}") # Use 'Name' as per data_handler

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


# --- Send Emails Button and Confirmation Flow ---
st.header("5. Send All Emails")

col1_send_btn, col2_send_conf = st.columns([1, 2])

with col1_send_btn:
    if st.button("Send All Emails", key="main_send_button"):
        log_message("MAIN 'Send All Emails' button clicked.")

        # Perform initial checks
        if not st.session_state.contacts:
            st.warning("Please upload an Excel file with valid contacts first.")
            log_message("Attempted send without contacts.", is_error=True)
            st.session_state.awaiting_confirmation = False # Reset if checks fail
        else:
            # Store current prompt and personalization mode for the send process
            # Use the .get() method to safely retrieve values from widgets' session_state
            st.session_state.user_prompt_for_send = st.session_state.get('prompt_input', '')
            st.session_state.personalized_mode_for_send = st.session_state.get('personalized_mode', False)