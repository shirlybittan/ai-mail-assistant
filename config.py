# config.py - Consolidated Secrets Access and Log Path

import streamlit as st
import os # Import the os module to access environment variables

# --- SECRETS CONFIGURATION ---
# Get the entire 'app_credentials' section as a dictionary from Streamlit Secrets
APP_CREDENTIALS = st.secrets.get("app_credentials", {})

# Extract individual credentials from the APP_CREDENTIALS dictionary
SENDER_EMAIL = APP_CREDENTIALS.get("SENDER_EMAIL")
SENDER_PASSWORD = APP_CREDENTIALS.get("SENDER_PASSWORD")
OPENAI_API_KEY = APP_CREDENTIALS.get("OPENAI_API_KEY")

# Now, create the SENDER_CREDENTIALS dictionary that your app expects
# It will contain only one email for now, if SENDER_EMAIL and SENDER_PASSWORD are found.
SENDER_CREDENTIALS = {}
if SENDER_EMAIL and SENDER_PASSWORD:
    SENDER_CREDENTIALS[SENDER_EMAIL] = SENDER_PASSWORD

# --- LOGGING CONFIGURATION ---
# Path for logging failed email attempts. This is not a secret.
FAILED_EMAILS_LOG_PATH = "failed_emails.log" # This path will be created in your app's root directory on Streamlit Cloud