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

def send_bulk_email_messages(sender_email, sender_name, messages, attachments=None):
    """
    Sends multiple transactional emails using 1 batch API call to Brevo for high throughput.
    
    :param sender_email:      The email address of the sender.
    :param sender_name:       The display name of the sender.
    :param messages:          List of dicts, each with keys: 'to_email', 'to_name', 'subject', 'body'.
    :param attachments:       Optional list of file paths to attach (applies to all messages).
    :return:                  Dict with status and response or error message.
    """
    # Validate messages
    if not messages:
        return {"status": "error", "message": "No messages provided"}

    total = len(messages)
    # Brevo limit: max 2000 recipients (versions) per batch
    if total > 2000:
        return {"status": "error", "message": f"Too many recipients ({total}). Brevo limit is 2000 recipients per batch."}

    # Configure API client
    configuration = sib_api_v3_sdk.Configuration()
    configuration.api_key['api-key'] = BREVO_API_KEY
    api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))

    # Prepare attachments once
    _attachments = []
    if attachments:
        for path in attachments:
            try:
                with open(path, "rb") as f:
                    data = f.read()
                encoded = base64.b64encode(data).decode('utf-8')
                _attachments.append({
                    "content": encoded,
                    "name": os.path.basename(path)
                })
            except Exception as e:
                print(f"Warning: could not read attachment {path}: {e}")
                # continue without this attachment

    # Build message versions
    versions = []
    for msg in messages:
        to_email = msg['to_email']
        to_name = msg.get('to_name', '')
        subject = msg.get('subject', '')
        body = msg.get('body', '')
        html_body = body.replace('\n', '<br>')

        versions.append({
            "to": [{"email": to_email, "name": to_name}],
            "subject": subject,
            "html_content": html_body
        })

    # Use first message to seed global defaults
    first = messages[0]
    global_html = first.get('body', '').replace('\n', '<br>')
    global_subject = first.get('subject', '')

    # Prepare batch payload
    send_args = {
        "sender": {"email": sender_email, "name": sender_name},
        "subject": global_subject,
        "html_content": global_html,
        "message_versions": versions
    }
    if _attachments:
        send_args["attachment"] = _attachments

    # Create SendSmtpEmail model
    batch_email = sib_api_v3_sdk.SendSmtpEmail(**send_args)

    # Call API
    try:
        response = api_instance.send_transac_email(batch_email)
        return {"status": "success", "message": "Bulk email sent successfully via Brevo.", "response": response}
    except ApiException as e:
        error_msg = f"Brevo API Error: {e.body}" if hasattr(e, 'body') else str(e)
        # Log each failure
        for msg in messages:
            _log_failed_email_to_file(
                sender_email,
                msg['to_email'],
                msg.get('subject', ''),
                msg.get('body', ''),
                error_msg,
                FAILED_EMAILS_LOG_PATH
            )
        return {"status": "error", "message": error_msg}
    except Exception as e:
        error_msg = f"Unexpected error: {e}"
        for msg in messages:
            _log_failed_email_to_file(
                sender_email,
                msg['to_email'],
                msg.get('subject', ''),
                msg.get('body', ''),
                error_msg,
                FAILED_EMAILS_LOG_PATH
            )
        return {"status": "error", "message": error_msg}
