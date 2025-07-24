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

def send_email_message(sender_email, sender_password, to_email, subject, body, attachments=None, log_path="failed_emails.log"):
    """
    Sends an email message with optional attachments using an SMTP server.

    Args:
        sender_email (str): The sender's email address.
        sender_password (str): The sender's app password (for Google, Outlook, etc.).
        to_email (str): The recipient's email address.
        subject (str): The subject of the email.
        body (str): The body content of the email, expected to be in HTML format.
        attachments (list, optional): A list of file paths to attach. Defaults to None.
        log_path (str, optional): Path to the file where failed emails should be logged.
                                  Defaults to "failed_emails.log".

    Returns:
        dict: A dictionary with 'status' ("success" or "error") and 'message'.
    """
    if not re.match(r"[^@]+@[^@]+\.[^@]+", to_email):
        _log_failed_email_to_file(sender_email, to_email, subject, body, "Invalid recipient email format", log_path)
        return {"status": "error", "message": "Invalid recipient email format."}

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = to_email
    msg['Subject'] = subject

    # --- FIX: Attach the body as HTML to preserve formatting ---
    msg.attach(MIMEText(body, 'html'))

    if attachments:
        for attachment_path in attachments:
            if not os.path.exists(attachment_path):
                error_msg = f"Attachment file not found: {attachment_path}"
                _log_failed_email_to_file(sender_email, to_email, subject, body, error_msg, log_path)
                return {"status": "error", "message": error_msg}

            try:
                with open(attachment_path, "rb") as attachment:
                    part = MIMEBase("application", "octet-stream")
                    part.set_payload(attachment.read())
                encoders.encode_base64(part)
                part.add_header(
                    "Content-Disposition",
                    f"attachment; filename= {os.path.basename(attachment_path)}",
                )
                msg.attach(part)
            except Exception as e:
                error_msg = f"Failed to attach file {os.path.basename(attachment_path)}: {e}"
                _log_failed_email_to_file(sender_email, to_email, subject, body, error_msg, log_path)
                return {"status": "error", "message": error_msg}

    try:
        if "gmail.com" in sender_email:
            smtp_server = "smtp.gmail.com"
            smtp_port = 587
        elif "outlook.com" in sender_email or "hotmail.com" in sender_email:
            smtp_server = "smtp.office365.com"
            smtp_port = 587
        else:
            _log_failed_email_to_file(sender_email, to_email, subject, body, "Unsupported sender email domain", log_path)
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
        error_msg = f"An unexpected error occurred during email sending: {e}"
        _log_failed_email_to_file(sender_email, to_email, subject, body, error_msg, log_path)
        return {"status": "error", "message": error_msg}