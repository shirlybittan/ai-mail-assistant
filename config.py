# config.py
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# OpenAI Credentials
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Yagmail (Gmail) Credentials
SENDER_EMAIL  = os.getenv("SENDER_EMAIL ")
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD")

# Logging settings
LOG_FILE_PATH = "sending_log.txt"
FAILED_EMAILS_LOG_PATH = "failed_emails_log.txt"

# GUI settings (optional, for future scalability)
# DEFAULT_WINDOW_GEOMETRY = "800x650"