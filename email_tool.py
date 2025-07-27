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
    Sends an email message with optional attachments, handling common SMTP errors
    and logging failures.
    """
    if attachments is None:
        attachments = []

    try:
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = to_email
        msg['Subject'] = subject

        # Convert plain text body with newlines to HTML with <br> tags
        # and attach it as HTML part
        html_body = body.replace('\n', '<br>')
        msg.attach(MIMEText(html_body, 'html'))

        # Add attachments
        for filepath in attachments:
            if os.path.exists(filepath):
                part = MIMEBase('application', 'octet-stream')
                with open(filepath, 'rb') as file:
                    part.set_payload(file.read())
                encoders.encode_base64(part)
                part.add_header('Content-Disposition',
                                f'attachment; filename= {os.path.basename(filepath)}')
                msg.attach(part)
            else:
                print(f"Warning: Attachment file not found - {filepath}")

        # Determine SMTP server and port based on sender email domain
        smtp_server = None
        smtp_port = None
        if "gmail.com" in sender_email:
            smtp_server = "smtp.gmail.com"
            smtp_port = 587
        elif "outlook.com" in sender_email or "hotmail.com" in sender_email:
            smtp_server = "smtp-mail.outlook.com"
            smtp_port = 587
        else:
            error_msg = "Unsupported sender email domain. Only Gmail and Outlook/Hotmail are currently supported."
            _log_failed_email_to_file(sender_email, to_email, subject, body, error_msg, log_path)
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