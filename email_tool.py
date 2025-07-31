# email_tool.py

import datetime
import os
import base64
import json
import logging

# Import Brevo SDK
import brevo_python as sib_api_v3_sdk
from brevo_python.rest import ApiException
from config import BREVO_API_KEY, FAILED_EMAILS_LOG_PATH # Import BREVO_API_KEY

# Set up logging for debugging - only show email_tool logs
logging.basicConfig(level=logging.WARNING)  # Set global level to WARNING to suppress most logs
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)  # Set email_tool logger to DEBUG level

# Suppress debug logs from specific noisy modules
logging.getLogger("httpcore").setLevel(logging.WARNING)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("openai").setLevel(logging.WARNING)
logging.getLogger("brevo_python").setLevel(logging.WARNING)

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

def _debug_log_email_parameters(send_smtp_email_args, function_name="send_email"):
    """Debug logging for email parameters"""
    logger.debug(f"=== {function_name.upper()} DEBUG INFO ===")
    logger.debug(f"Timestamp: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.debug(f"API Key (first 10 chars): {BREVO_API_KEY[:10]}..." if BREVO_API_KEY else "API Key: NOT SET")
    
    # Log all parameters
    for key, value in send_smtp_email_args.items():
        if key == "attachment" and value:
            logger.debug(f"Attachments: {len(value)} files")
            for i, attachment in enumerate(value):
                logger.debug(f"  Attachment {i+1}: {attachment.get('name', 'Unknown')} ({len(attachment.get('content', ''))} chars)")
        elif key == "html_content":
            logger.debug(f"HTML Content Length: {len(value)} characters")
            logger.debug(f"HTML Content Preview: {value[:200]}...")
        else:
            logger.debug(f"{key}: {value}")
    
    logger.debug("=" * 50)

def send_email_message(sender_email, sender_name, to_email, to_name, subject, body, attachments=None):
    """
    Sends an email using the Brevo (Sendinblue) API.
    """
    logger.debug(f"Starting single email send to: {to_email}")
    
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
                    logger.debug(f"Successfully processed attachment: {os.path.basename(attachment_path)} ({len(file_content)} bytes)")
            except Exception as e:
                logger.error(f"Warning: Could not read attachment {attachment_path}: {e}")
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

    # Debug logging
    _debug_log_email_parameters(send_smtp_email_args, "send_email_message")

    send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(**send_smtp_email_args)

    try:
        logger.debug("Making Brevo API call...")
        api_response = api_instance.send_transac_email(send_smtp_email)
        logger.debug(f"Brevo API Response: {api_response}")
        logger.info(f"Email sent successfully to {to_email}")
        return {"status": "success", "message": "Email sent successfully via Brevo."}
    except ApiException as e:
        error_msg = f"Brevo API Error: {e.body}"
        logger.error(f"Brevo API Exception: {e}")
        logger.error(f"Error body: {e.body}")
        logger.error(f"Error status: {e.status}")
        _log_failed_email_to_file(sender_email, to_email, subject, body, error_msg, FAILED_EMAILS_LOG_PATH)
        return {"status": "error", "message": error_msg}
    except Exception as e:
        error_msg = f"An unexpected error occurred: {e}"
        logger.error(f"Unexpected error: {e}")
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
    logger.debug(f"Starting bulk email send to {len(messages)} recipients")
    
    # Validate messages
    if not messages:
        logger.error("No messages provided for bulk send")
        return {"status": "error", "message": "No messages provided"}

    total = len(messages)
    logger.debug(f"Total messages to send: {total}")
    
    # Brevo limit: max 2000 recipients (versions) per batch
    if total > 2000:
        logger.error(f"Too many recipients ({total}). Brevo limit is 2000 recipients per batch.")
        return {"status": "error", "message": f"Too many recipients ({total}). Brevo limit is 2000 recipients per batch."}

    # Configure API client
    configuration = sib_api_v3_sdk.Configuration()
    configuration.api_key['api-key'] = BREVO_API_KEY
    api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))

    # Prepare attachments once
    _attachments = []
    if attachments:
        logger.debug(f"Processing {len(attachments)} attachments")
        for path in attachments:
            try:
                with open(path, "rb") as f:
                    data = f.read()
                encoded = base64.b64encode(data).decode('utf-8')
                _attachments.append({
                    "content": encoded,
                    "name": os.path.basename(path)
                })
                logger.debug(f"Successfully processed attachment: {os.path.basename(path)} ({len(data)} bytes)")
            except Exception as e:
                logger.error(f"Warning: could not read attachment {path}: {e}")
                # continue without this attachment

    # Build message versions
    versions = []
    logger.debug("Building message versions...")
    for i, msg in enumerate(messages):
        to_email = msg['to_email']
        to_name = msg.get('to_name', '')
        subject = msg.get('subject', '')
        body = msg.get('body', '')
        html_body = body.replace('\n', '<br>')

        version = {
            "to": [{"email": to_email, "name": to_name}],
            "subject": subject,
            "html_content": html_body
        }
        versions.append(version)
        
        logger.debug(f"Version {i+1}: {to_email} - Subject: {subject[:50]}... - Body length: {len(html_body)}")

    # Use first message to seed global defaults
    first = messages[0]
    global_html = first.get('body', '').replace('\n', '<br>')
    global_subject = first.get('subject', '')
    
    logger.debug(f"Global subject: {global_subject}")
    logger.debug(f"Global HTML length: {len(global_html)}")

    # Prepare batch payload
    send_args = {
        "sender": {"email": sender_email, "name": sender_name},
        "subject": global_subject,
        "html_content": global_html,
        "message_versions": versions
    }
    if _attachments:
        send_args["attachment"] = _attachments

    # Debug logging for bulk send
    _debug_log_email_parameters(send_args, "send_bulk_email_messages")
    logger.debug(f"Number of message versions: {len(versions)}")

    # Create SendSmtpEmail model
    batch_email = sib_api_v3_sdk.SendSmtpEmail(**send_args)

    # Call API
    try:
        logger.debug("Making Brevo bulk API call...")
        response = api_instance.send_transac_email(batch_email)
        logger.debug(f"Brevo bulk API Response: {response}")
        logger.info(f"Bulk email sent successfully to {total} recipients")
        return {"status": "success", "message": "Bulk email sent successfully via Brevo.", "response": response}
    except ApiException as e:
        error_msg = f"Brevo API Error: {e.body}" if hasattr(e, 'body') else str(e)
        logger.error(f"Brevo API Exception: {e}")
        logger.error(f"Error body: {e.body if hasattr(e, 'body') else 'No body'}")
        logger.error(f"Error status: {e.status if hasattr(e, 'status') else 'No status'}")
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
        logger.error(f"Unexpected error in bulk send: {e}")
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
