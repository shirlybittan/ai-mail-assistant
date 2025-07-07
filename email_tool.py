# email_tool.py
import yagmail
import datetime
import os

# Import configuration variables
# Ensure config.py is in the same directory or accessible in Python path
try:
    from config import SENDER_EMAIL, SENDER_PASSWORD, FAILED_EMAILS_LOG_PATH
    # Add a print to confirm successful imports in email_tool.py
    print("CONSOLE LOG: email_tool.py: Config variables imported successfully.")
    # Verify credentials are not empty within this module
    if not SENDER_EMAIL:
        print("CRITICAL ERROR: email_tool.py: SENDER_EMAIL is not set.")
    if not SENDER_PASSWORD:
        print("CRITICAL ERROR: email_tool.py: SENDER_PASSWORD is not set.")
except ImportError as e:
    print(f"CRITICAL ERROR: email_tool.py: Failed to import config: {e}")
    SENDER_EMAIL = None
    SENDER_PASSWORD = None
except Exception as e:
    print(f"CRITICAL ERROR: email_tool.py: An unexpected error occurred during config import: {e}")
    SENDER_EMAIL = None
    SENDER_PASSWORD = None


def _log_failed_email_to_file(to_email, subject, body, error_message):
    """Logs details of a failed email attempt to a dedicated file."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = (
        f"[{timestamp}] To: {to_email}, Subject: {subject}\n"
        f"Error: {error_message}\n"
        f"Body Snippet: {body[:200]}...\n" # Log first 200 chars of body
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


def send_email_message(to_email: str, subject: str, body: str) -> dict:
    """
    Sends an email using yagmail.
    Returns a dictionary indicating status and message.
    """
    if not SENDER_EMAIL or not SENDER_PASSWORD:
        error_msg = "Email sender credentials (SENDER_EMAIL or SENDER_PASSWORD) are not configured."
        _log_failed_email_to_file(to_email, subject, body, error_msg)
        print(f"ERROR: email_tool.py: {error_msg}")
        return {"status": "failed", "message": error_msg}

    try:
        print(f"CONSOLE LOG: email_tool.py: Attempting to send email from {SENDER_EMAIL} to {to_email}...")
        # Initialize yagmail SMTP client
        # yagmail automatically detects common SMTP servers (like Gmail)
        # You can specify host='smtp.gmail.com', port=587 if needed, but usually not for Gmail
        yag = yagmail.SMTP(user=SENDER_EMAIL, password=SENDER_PASSWORD)
        
        # Send the email
        yag.send(
            to=to_email,
            subject=subject,
            contents=body
        )
        print(f"CONSOLE LOG: email_tool.py: yagmail.send() call completed for {to_email}.")
        return {"status": "success", "message": "Email sent successfully."}

    except yagmail.YagAuthenticationError as e:
        error_msg = f"Authentication failed. Check SENDER_EMAIL and SENDER_PASSWORD (App Password for Gmail with 2FA?). Error: {e}"
        _log_failed_email_to_file(to_email, subject, body, error_msg)
        print(f"ERROR: email_tool.py: {error_msg}")
        return {"status": "failed", "message": error_msg}
    except yagmail.YagConnectionError as e:
        error_msg = f"Connection error to SMTP server. Check internet connection or SMTP settings. Error: {e}"
        _log_failed_email_to_file(to_email, subject, body, error_msg)
        print(f"ERROR: email_tool.py: {error_msg}")
        return {"status": "failed", "message": error_msg}
    except Exception as e:
        error_msg = f"An unexpected error occurred while sending email: {e}"
        _log_failed_email_to_file(to_email, subject, body, error_msg)
        print(f"ERROR: email_tool.py: {error_msg}")
        return {"status": "failed", "message": error_msg}