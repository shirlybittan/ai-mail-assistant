# email_tool.py

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import datetime
import re
import os # Import os for path manipulation


def _log_failed_email_to_file(sender_email, to_email, subject, body, error_message, log_path):
    """Logs details of a failed email attempt to a dedicated file."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = (
        f"Timestamp: {timestamp}\n"
        f"Sender: {sender_email}\n"
        f"Recipient: {to_email}\n"
        f"Subject: {subject}\n"
        f"Error: {error_message}\n"
        f"Body Snippet (first 200 chars): {body[:200]}...\n"
        f"{'-'*50}\n\n"
    )
    # Ensure the directory for the log file exists if it's a relative path
    log_dir = os.path.dirname(log_path)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir)

    with open(log_path, "a", encoding="utf-8") as f:
        f.write(log_entry)

def send_email_message(sender_email, sender_password, to_email, subject, body, log_path, attachments=None):
    """
    Sends an email message with optional attachments using SMTP.
    The body is now expected to be HTML.
    """
    if attachments is None:
        attachments = []

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = to_email
    msg['Subject'] = subject

    # Attach the HTML body
    msg.attach(MIMEText(body, 'html')) # Changed 'plain' to 'html'

    for attachment_data, attachment_name in attachments:
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(attachment_data)
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f'attachment; filename="{attachment_name}"')
        msg.attach(part)

    try:
        smtp_server = ""
        smtp_port = 0

        # Determine SMTP server and port based on sender email domain
        if "@gmail.com" in sender_email:
            smtp_server = "smtp.gmail.com"
            smtp_port = 587
        elif "@outlook.com" in sender_email or "@hotmail.com" in sender_email:
            smtp_server = "smtp.office365.com" # Common for Outlook/Hotmail
            smtp_port = 587
        else:
            return {"status": "error", "message": "Unsupported sender email domain. Only Gmail and Outlook/Hotmail are currently supported."}

        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)
        return {"status": "success", "message": "Email sent successfully."}

    except smtplib.SMTPAuthenticationError as e:
        error_msg = f"SMTP Authentication Error: {e}. Check email/password or app password settings."
        _log_failed_email_to_file(sender_email, to_email, subject, body, error_msg, log_path)
        return {"status": "error", "message": error_msg}
    except smtplib.SMTPConnectError as e:
        error_msg = f"SMTP Connection Error: {e}. Check server address or network."
        _log_failed_email_to_file(sender_email, to_email, subject, body, error_msg, log_path)
        return {"status": "error", "message": error_msg}
    except smtplib.SMTPException as e:
        error_msg = f"SMTP Error: {e}. A general SMTP error occurred."
        _log_failed_email_to_file(sender_email, to_email, subject, body, error_msg, log_path)
        return {"status": "error", "message": error_msg}
    except Exception as e:
        error_msg = f"An unexpected error occurred: {e}. Ensure all inputs are valid."
        _log_failed_email_to_file(sender_email, to_email, subject, body, error_msg, log_path)
        return {"status": "error", "message": error_msg}

if __name__ == '__main__':
    # Example usage for testing
    # You would typically get these from Streamlit secrets or environment variables
    test_sender_email = os.getenv("GMAIL_USER")
    test_sender_password = os.getenv("GMAIL_APP_PASSWORD") # Use app password for Gmail
    test_to_email = "recipient@example.com"
    test_subject = "Test HTML Email from Python"
    test_body_html = """
    <html>
    <body>
        <p>Hello <b>World</b>,</p>
        <p>This is a test HTML email sent from a Python script.</p>
        <p>Regards,<br>Your App</p>
    </body>
    </html>
    """
    test_log_path = "test_failed_emails.log"

    print("Attempting to send test email...")
    if test_sender_email and test_sender_password:
        result = send_email_message(
            sender_email=test_sender_email,
            sender_password=test_sender_password,
            to_email=test_to_email,
            subject=test_subject,
            body=test_body_html,
            log_path=test_log_path,
            attachments=[]
        )
        print(f"Test email result: {result}")
    else:
        print("Skipping email send test: GMAIL_USER or GMAIL_APP_PASSWORD not set in environment.")