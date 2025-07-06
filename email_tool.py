# email_tool.py 
import os
import yagmail
import datetime # Added for timestamping logs

# Import from config.py
from config import GMAIL_USER, GMAIL_APP_PASSWORD, FAILED_EMAILS_LOG_PATH

def _log_failed_email_to_file(to_email: str, subject: str, body: str, reason: str):
    """Logs details of a failed email to a local text file."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] FAILED EMAIL TO: {to_email}\n" \
                f"  Reason: {reason}\n" \
                f"  Subject: {subject}\n" \
                f"  Body:\n{body}\n" \
                f"--- END FAILED EMAIL ---\n\n"
    try:
        with open(FAILED_EMAILS_LOG_PATH, "a", encoding="utf-8") as f:
            f.write(log_entry)
    except Exception as e:
        print(f"Error writing to failed emails log file: {e}")

def send_email_message(to_email: str, subject: str, body: str) -> dict:
    """Sends an email via Yagmail (Gmail SMTP)."""
    
    if not all([GMAIL_USER, GMAIL_APP_PASSWORD]):
        return {"status": "error", "message": "Gmail credentials (GMAIL_USER, GMAIL_APP_PASSWORD) not fully configured in .env.", "log_to_file": True}
    if not to_email.strip():
        return {"status": "error", "message": "Email 'to_email' cannot be empty.", "log_to_file": False} # Don't log if recipient is empty
    if not subject.strip():
        return {"status": "error", "message": "Email subject cannot be empty.", "log_to_file": True}
    if not body.strip():
        return {"status": "error", "message": "Email body cannot be empty.", "log_to_file": True}
    
    # Basic email format validation (can be more robust but this is a start)
    if "@" not in to_email or "." not in to_email.split('@')[-1]:
        return {"status": "error", "message": f"Invalid email format for: {to_email}", "log_to_file": False} # Don't log if format is invalid

    try:
        yag = yagmail.SMTP(user=GMAIL_USER, password=GMAIL_APP_PASSWORD)
        
        yag.send(
            to=to_email,
            subject=subject,
            contents=body,
        )
        return {"status": "success", "message": f"Email sent to {to_email} successfully.", "log_to_file": False}
    except yagmail.YagAddressError as e:
        _log_failed_email_to_file(to_email, subject, body, f"Invalid address: {e}")
        return {"status": "error", "message": f"Invalid sender or recipient email address: {e}", "log_to_file": True}
    except yagmail.YagConnectionError as e:
        _log_failed_email_to_file(to_email, subject, body, f"Connection error: {e}")
        return {"status": "error", "message": f"Could not connect to Gmail SMTP server. Check internet or app password: {e}", "log_to_file": True}
    except Exception as e:
        _log_failed_email_to_file(to_email, subject, body, f"Unknown error: {e}")
        return {"status": "error", "message": f"Failed to send email: {e}. Ensure 2FA is on and App Password is correct.", "log_to_file": True}

if __name__ == '__main__':
    print("--- Testing Email Tool (requires valid Gmail credentials and App Password) ---")

    # Example Email Test (UNCOMMENT TO RUN AND REPLACE WITH REAL DATA)
    # Be careful with limits if testing too much!
    # email_test_result = send_email_message(
    #     "your_test_recipient@example.com", # Replace with an actual email you can check
    #     "Smart Email Messenger Test Subject (Yagmail)",
    #     "This is a test email from your Smart Email Messenger AI agent using Yagmail. If you received this, the email tool works!"
    # )
    # print(email_test_result)