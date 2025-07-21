# config.py
import streamlit as st
import os

# Get sender credentials dictionary from Streamlit secrets
# This will be a dictionary where keys are emails and values are passwords
SENDER_CREDENTIALS = st.secrets.get("SENDER_CREDENTIALS", {})

# Get OpenAI API Key
OPENAI_API_KEY = st.secrets.get("OPENAI_API_KEY")

# Path for logging failed emails (adjust if you want this elsewhere)
FAILED_EMAILS_LOG_PATH = "failed_emails_log.txt"

# Ensure essential credentials are not empty
if not SENDER_CREDENTIALS:
    print("CRITICAL ERROR: config.py: SENDER_CREDENTIALS not found in Streamlit secrets.")
if not OPENAI_API_KEY:
    print("CRITICAL ERROR: config.py: OPENAI_API_KEY not found in Streamlit secrets.")