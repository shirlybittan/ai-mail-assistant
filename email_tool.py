# email_tool.py
import yagmail
import datetime
import os
import re

# We import FAILED_EMAILS_LOG_PATH from config.py for logging purposes
from config import FAILED_EMAILS_LOG_PATH

def _log_failed_email_to_file(sender_email, to_email, subject, body, error_message):
    """Logs details of a failed email attempt to a dedicated file."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = (
        f"[{timestamp}] From: {sender_email}, To: {to_email}, Subject: {subject}\n"
        f"Error: {error_message}\n"
        f"--------------------------------------------------\n"
    )
    try:
        log_dir = os.path.dirname(FAILED_EMAILS_LOG_PATH)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)
            print(f"DEBUG: email_tool.py: Created failed emails log directory: {log_dir}")
        with open(FAILED_EMAILS_LOG_PATH, "a", encoding="utf-8") as f:
            f.write(log_entry)
            f.flush()
        print(f"CONSOLE LOG: email_tool.py: Logged failed email to {FAILED_EMAILS_LOG_PATH} for {to_email}.")
    except Exception as e:
        print(f"ERROR: email_tool.py: Could not write to failed emails log file '{FAILED_EMAILS_LOG_PATH}': {e}")


def send_email_message(sender_email: str, sender_password: str, to_email: str, subject: str, body: str) -> dict:
    """
    Sends an email using yagmail with dynamically provided sender credentials.
    Returns a dictionary indicating status and message.
    """
    if not sender_email or not sender_password:
        error_msg = "Email sender credentials (sender_email or sender_password) are not provided."
        _log_failed_email_to_file(sender_email, to_email, subject, body, error_msg)
        print(f"ERROR: email_tool.py: {error_msg}")
        return {"status": "failed", "message": error_msg}

    # Basic validation for the recipient email format
    if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', to_email):
        error_msg = f"Invalid recipient email format: {to_email}"
        _log_failed_email_to_file(sender_email, to_email, subject, body, error_msg)
        print(f"ERROR: email_tool.py: {error_msg}")
        return {"status": "failed", "message": error_msg}

    try:
        print(f"CONSOLE LOG: email_tool.py: Attempting to send email from {sender_email} to {to_email}...")
        
        # Initialize yagmail SMTP client with provided credentials
        yag = yagmail.SMTP(user=sender_email, password=sender_password)
        
        # Send the email
        yag.send(
            to=to_email,
            subject=subject,
            contents=body
        )
        print(f"CONSOLE LOG: email_tool.py: yagmail.send() call completed for {to_email}.")
        return {"status": "success", "message": "Email sent successfully."}

    except yagmail.YagAuthenticationError as e:
        error_msg = f"Authentication failed for {sender_email}. Check credentials (App Password for Gmail with 2FA?). Error: {e}"
        _log_failed_email_to_file(sender_email, to_email, subject, body, error_msg)
        print(f"ERROR: email_tool.py: {error_msg}")
        return {"status": "failed", "message": error_msg}
    except yagmail.YagConnectionError as e:
        error_msg = f"Connection error to SMTP server for {sender_email}. Check internet connection or SMTP settings. Error: {e}"
        _log_failed_email_to_file(sender_email, to_email, subject, body, error_msg)
        print(f"ERROR: email_tool.py: {error_msg}")
        return {"status": "failed", "message": error_msg}
    except Exception as e:
        error_msg = f"An unexpected error occurred while sending email from {sender_email}: {e}"
        _log_failed_email_to_file(sender_email, to_email, subject, body, error_msg)
        print(f"ERROR: email_tool.py: {error_msg}")
        return {"status": "failed", "message": error_msg}