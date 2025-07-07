# email_tool.py (excerpt)
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import datetime
from config import SENDER_EMAIL, SENDER_PASSWORD, FAILED_EMAILS_LOG_PATH # Ensure this import

def _log_failed_email_to_file(to_email, subject, body, error_message):
    try:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = (
            f"Timestamp: {timestamp}\n"
            f"To: {to_email}\n"
            f"Subject: {subject}\n"
            f"Body (partial): {body[:200]}...\n" # Log only a partial body to avoid huge logs
            f"Error: {error_message}\n"
            f"{'-'*50}\n"
        )
        with open(FAILED_EMAILS_LOG_PATH, "a", encoding="utf-8") as f:
            f.write(log_entry)
    except Exception as e:
        print(f"ERROR: Could not log failed email to file: {e}") # This print is important if _log_failed_email fails!

def send_email_message(to_email, subject, body):
    # ... (your existing email sending logic) ...
    try:
        # ... (SMTP setup, sending) ...
        return {"status": "success", "message": "Email sent successfully!"}
    except Exception as e:
        error_message = str(e)
        _log_failed_email_to_file(to_email, subject, body, error_message) # Call the helper
        return {"status": "error", "message": f"Failed to send email: {error_message}"}