# config.py - Consolidated Secrets Access and Log Path

import streamlit as st
import os # Import the os module to access environment variables

# --- SECRETS CONFIGURATION ---
# Get the entire 'app_credentials' section as a dictionary from Streamlit Secrets
APP_CREDENTIALS = st.secrets.get("app_credentials", {})

# Extract individual credentials from the APP_CREDENTIALS dictionary
SENDER_EMAIL = APP_CREDENTIALS.get("SENDER_EMAIL")
# SENDER_PASSWORD is no longer needed for Brevo API authentication.
OPENAI_API_KEY = APP_CREDENTIALS.get("OPENAI_API_KEY")
BREVO_API_KEY = APP_CREDENTIALS.get("BREVO_API_KEY")

# The SENDER_CREDENTIALS dictionary is also no longer necessary
# as Brevo uses API keys for authentication.

# --- LOGGING CONFIGURATION ---
# Path for logging failed email attempts. This is not a secret.
FAILED_EMAILS_LOG_PATH = "failed_emails.log" # This path will be created in your app's root directory on Streamlit Cloud