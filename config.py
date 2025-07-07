# config.py
import os

# Define the base directory of your project (where config.py is located)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Define log file paths relative to BASE_DIR
LOG_FILE_PATH = os.path.join(BASE_DIR, 'sending_log.txt') # Changed to sending_log.txt for clarity
FAILED_EMAILS_LOG_PATH = os.path.join(BASE_DIR, 'failed_emails_log.txt')

# Your email credentials
# It's HIGHLY RECOMMENDED to use Streamlit Secrets or environment variables
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD") # This should be your App Password

# OpenAI API Key (if not already set as an environment variable in Streamlit Cloud)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Add a check for essential variables
if not SENDER_EMAIL or not SENDER_PASSWORD:
    print("WARNING: SENDER_EMAIL or SENDER_PASSWORD environment variables are not set in config.py or Streamlit Secrets.")
    print("Email sending will fail.")

if not OPENAI_API_KEY:
    print("WARNING: OPENAI_API_KEY environment variable is not set. AI functions may not work.")