# config.py
import os

# Define the base directory of your project (where config.py is located)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Define log file paths relative to BASE_DIR
LOG_FILE_PATH = os.path.join(BASE_DIR, 'sending_log.txt')
FAILED_EMAILS_LOG_PATH = os.path.join(BASE_DIR, 'failed_emails_log.txt')

# Retrieve sensitive information from Streamlit Secrets / Environment variables
# Use .get() for safety, but then explicitly check for None
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Explicitly check and raise an error if critical environment variables are not set
if not SENDER_EMAIL:
    raise ValueError("Streamlit Secret 'SENDER_EMAIL' is not set or not accessible. Please configure it in your Streamlit Cloud app settings.")
if not SENDER_PASSWORD:
    raise ValueError("Streamlit Secret 'SENDER_PASSWORD' is not set or not accessible. Please configure it in your Streamlit Cloud app settings (use an App Password).")
if not OPENAI_API_KEY:
    raise ValueError("Streamlit Secret 'OPENAI_API_KEY' is not set or not accessible. Please configure it in your Streamlit Cloud app settings.")

# (Optional) Ensure log directory exists, though streamlit_app.py also handles this.
# _log_dir = os.path.dirname(LOG_FILE_PATH)
# if not os.path.exists(_log_dir):
#     os.makedirs(_log_dir, exist_ok=True)