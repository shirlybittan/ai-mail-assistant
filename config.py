# config.py - Consolidated Secrets Access

import streamlit as st

# Get the entire 'app_credentials' section as a dictionary
APP_CREDENTIALS = st.secrets.get("app_credentials", {})

# Extract individual credentials from the APP_CREDENTIALS dictionary
SENDER_EMAIL = APP_CREDENTIALS.get("SENDER_EMAIL")
SENDER_PASSWORD = APP_CREDENTIALS.get("SENDER_PASSWORD")
OPENAI_API_KEY = APP_CREDENTIALS.get("OPENAI_API_KEY")

# Now, create the SENDER_CREDENTIALS dictionary that your app expects
# It will contain only one email for now.
SENDER_CREDENTIALS = {}
if SENDER_EMAIL and SENDER_PASSWORD:
    SENDER_CREDENTIALS[SENDER_EMAIL] = SENDER_PASSWORD

# For debugging (these will show in your Streamlit Cloud app's UI if still in streamlit_app.py)
# print(f"DEBUG_CONFIG: Raw APP_CREDENTIALS: {APP_CREDENTIALS}")
# print(f"DEBUG_CONFIG: SENDER_EMAIL: {SENDER_EMAIL}")
# print(f"DEBUG_CONFIG: SENDER_PASSWORD: {bool(SENDER_PASSWORD)}") # Only show if it's there
# print(f"DEBUG_CONFIG: OPENAI_API_KEY: {bool(OPENAI_API_KEY)}") # Only show if it's there