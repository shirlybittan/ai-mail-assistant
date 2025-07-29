# email_tool.py

import datetime
import os
import base64

# Import Brevo SDK
import brevo_python as sib_api_v3_sdk
from brevo_python.rest import ApiException
from config import BREVO_API_KEY, FAILED_EMAILS_LOG_PATH # Import BREVO_API_KEY

def _log_failed_email_to_file(sender_email, to_email, subject, body, error_message, log_path=FAILED_EMAILS_LOG_PATH):
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
    log_dir = os.path.dirname(log_path)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir)

    with open(log_path, "a", encoding="utf-8") as f:
        f.write(log_entry)


def send_email_message(sender_email, sender_name, to_email, to_name, subject, body, attachments=None):
    """
    Sends an email using the Brevo (Sendinblue) API.
    """
    configuration = sib_api_v3_sdk.Configuration()
    configuration.api_key['api-key'] = BREVO_API_KEY

    api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))

    to = [{"email": to_email, "name": to_name}]
    sender = {"email": sender_email, "name": sender_name}

    _attachments = []
    if attachments: # 'attachments' is the function parameter, a list of file paths
        for attachment_path in attachments:
            try:
                with open(attachment_path, "rb") as f:
                    file_content = f.read()
                    encoded_content = base64.b64encode(file_content).decode('utf-8')
                    _attachments.append({
                        "content": encoded_content,
                        "name": os.path.basename(attachment_path)
                    })
            except Exception as e:
                print(f"Warning: Could not read attachment {attachment_path}: {e}")
                _log_failed_email_to_file(sender_email, to_email, subject, body, f"Attachment error for {os.path.basename(attachment_path)}: {e}", FAILED_EMAILS_LOG_PATH)
                continue

    # Convert newlines to HTML break tags for proper formatting in email
    html_body = body.replace('\n', '<br>')

    # Conditionally add 'attachment' parameter to SendSmtpEmail constructor
    send_smtp_email_args = {
        "to": to,
        "sender": sender,
        "subject": subject,
        "html_content": html_body, # Use the HTML-formatted body
    }

    if _attachments: # Only add if there are actual attachments
        send_smtp_email_args["attachment"] = _attachments

    send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(**send_smtp_email_args)

    try:
        api_response = api_instance.send_transac_email(send_smtp_email)
        return {"status": "success", "message": "Email sent successfully via Brevo."}
    except ApiException as e:
        error_msg = f"Brevo API Error: {e.body}"
        _log_failed_email_to_file(sender_email, to_email, subject, body, error_msg, FAILED_EMAILS_LOG_PATH)
        return {"status": "error", "message": error_msg}
    except Exception as e:
        error_msg = f"An unexpected error occurred: {e}"
        _log_failed_email_to_file(sender_email, to_email, subject, body, error_msg, FAILED_EMAILS_LOG_PATH)
        return {"status": "error", "message": error_msg}