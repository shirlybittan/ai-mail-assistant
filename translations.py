# translations.py

LANGUAGES = {
    "en": "English",
    "fr": "Français",
}

# This dictionary holds your translations.
# The structure is: {language_code: {key: translation_string}}
TRANSLATIONS = {
    "en": {
        "AI Email Assistant": "AI Email Assistant",
        "Welcome to the AI Email Assistant!": "Welcome to the AI Email Assistant!",
        "Select your language": "Select your language",
        "Generate Email": "Generate Email",
        "Compose your email details below.": "Compose your email details below.",
        "Recipient": "Recipient",
        "Subject": "Subject",
        "Body": "Body",
        "Sender": "Sender",
        "Clear Form": "Clear Form",
        "Your email has been generated!": "Your email has been generated!",
        "Error generating email. Please try again.": "Error generating email. Please try again.",
        "Recipient, Subject, and Body cannot be empty.": "Recipient, Subject, and Body cannot be empty.",
        "Enter a recipient": "Enter a recipient",
        "Enter a subject": "Enter a subject",
        "Enter email body": "Enter email body",
        "Enter sender name or email": "Enter sender name or email",
        # New Translations
        "1. Email Generation": "1. Email Generation",
        "Upload an Excel file with contacts (.xlsx)": "Upload an Excel file with contacts (.xlsx)",
        "Successfully loaded {count} valid contacts.": "Successfully loaded {count} valid contacts.",
        "WARNING: Some contacts had issues (e.g., missing/invalid/duplicate emails). They will be skipped.": "WARNING: Some contacts had issues (e.g., missing/invalid/duplicate emails). They will be skipped.",
        "Show Contact Issues": "Show Contact Issues",
        "No valid contacts loaded. Please check the issues below.": "No valid contacts loaded. Please check the issues below.",
        "No contacts found in the uploaded file or file was empty.": "No contacts found in the uploaded file or file was empty.",
        "What kind of email do you want to generate?": "What kind of email do you want to generate?",
        "e.g., 'A welcome email for new customers, offering a 10% discount.'": "e.g., 'A welcome email for new customers, offering a 10% discount.'",
        "Any specific style, tone, or information to include?": "Any specific style, tone, or information to include?",
        "e.g., 'Formal tone, mention our website: example.com. Use placeholders for Name and Email.'": "e.g., 'Formal tone, mention our website: example.com. Use placeholders for Name and Email.'",
        "Attach files (optional)": "Attach files (optional)",
        "Drag and drop files here": "Drag and drop files here",
        "Currently attached files:": "Currently attached files:",
        "Remove": "Remove",
        "Clear All Attachments": "Clear All Attachments",
        "Personalize emails for each recipient (replaces {{Name}}, {{Email}})": "Personalize emails for each recipient (replaces {{Name}}, {{Email}})",
        "Proceed to Review & Send": "Proceed to Review & Send",
        "Subject and Body cannot be empty to proceed.": "Subject and Body cannot be empty to proceed.",
        "2. Review & Send": "2. Review & Send",
        "Review your email content and contacts before sending.": "Review your email content and contacts before sending.",
        "Email Preview (First Contact)": "Email Preview (First Contact)",
        "No contacts loaded to show a preview.": "No contacts loaded to show a preview.",
        "Attached Files": "Attached Files",
        "Contacts Overview": "Contacts Overview",
        "{count} valid contacts loaded.": "{count} valid contacts loaded.",
        "Back to Edit Email": "Back to Edit Email",
        "Send All Emails": "Send All Emails",
        "3. Results": "3. Results",
        "Start New Email Session": "Start New Email Session",
        "All emails sent successfully!": "All emails sent successfully!",
        "All {count} emails were sent without any issues.": "All {count} emails were sent without any issues.",
        "Sending complete with errors.": "Sending complete with errors.",
        "Some emails failed to send. Please check the log below for details.": "Some emails failed to send. Please check the log below for details.",
        "No emails were sent. Please upload contacts and generate an email first.": "No emails were sent. Please upload contacts and generate an email first.",
        "Total Contacts": "Total Contacts",
        "Emails Successfully Sent": "Emails Successfully Sent",
        "Emails Failed to Send": "Emails Failed to Send",
        "Show Activity Log and Errors": "Show Activity Log and Errors",
        "Download Failed Emails Log": "Download Failed Emails Log",
        "Settings": "Settings",
        "This tool helps you generate and send personalized emails efficiently.": "This tool helps you generate and send personalized emails efficiently.",
        "Sender Email: {email} (Configured in secrets)": "Sender Email: {email} (Configured in secrets)",
        "Sender email is not configured. Please set SENDER_EMAIL and SENDER_PASSWORD in your Streamlit secrets.": "Sender email is not configured. Please set SENDER_EMAIL and SENDER_PASSWORD in your Streamlit secrets.",
        "Drag and drop file here": "Drag and drop file here",
        "Please provide a prompt to generate the email.": "Please provide a prompt to generate the email.",
        "Generating email content...": "Generating email content...",
        "Email content generated successfully.": "Email content generated successfully.",
        "Error generating email: {error_message}": "Error generating email: {error_message}",
        "No contacts loaded. Please upload a contact list first.": "No contacts loaded. Please upload a contact list first.",
        "Email subject or body is empty. Please generate email content first.": "Email subject or body is empty. Please generate email content first.",
        "Email sending process initiated...": "Email sending process initiated...",
        "Temporary directory created for attachments: {temp_dir}": "Temporary directory created for attachments: {temp_dir}",
        "Skipping invalid attachment: {attachment_path}": "Skipping invalid attachment: {attachment_path}",
        "Skipping contact {name} due to missing email.": "Skipping contact {name} due to missing email.",
        "--- [{current_num}/{total_num}] Processing contact: {name} ({email}) ---": "--- [{current_num}/{total_num}] Processing contact: {name} ({email}) ---",
        "Generating personalized email for {name}...": "Generating personalized email for {name}...",
        "Error personalizing email for {name}: {error_message}": "Error personalizing email for {name}: {error_message}",
        "Attempting Email for {name}...": "Attempting Email for {name}...",
        "Email sent to {recipient_email} successfully.": "Email sent to {recipient_email} successfully.",
        "Failed to send to {recipient_email}. Details: {message}": "Failed to send to {recipient_email}. Details: {message}",
        "An unexpected error occurred during email sending: {error_message}": "An unexpected error occurred during email sending: {error_message}",
        "--- Email sending process complete ---": "--- Email sending process complete ---",
        "Summary: {successful_count} successful, {failed_count} failed/skipped.": "Summary: {successful_count} successful, {failed_count} failed/skipped.",
        "Temporary directory deleted: {temp_dir}": "Temporary directory deleted: {temp_dir}",
        "Error deleting temporary directory {temp_dir}: {error_message}": "Error deleting temporary directory {temp_dir}: {error_message}",
        "Configuration Error: {error_message}. Please ensure OPENAI_API_KEY is set in your Streamlit secrets.": "Configuration Error: {error_message}. Please ensure OPENAI_API_KEY is set in your Streamlit secrets.",
        "Session state cleared.": "Session state cleared.",
        "Temporary Excel file deleted: {file_path}": "Temporary Excel file deleted: {file_path}",
        "Error deleting temporary Excel file {file_path}: {error_message}": "Error deleting temporary Excel file {file_path}: {error_message}",
        "Contact {index}": "Contact {index}"
    },
    "fr": {
        "AI Email Assistant": "Assistant d'E-mail IA",
        "Welcome to the AI Email Assistant!": "Bienvenue dans l'Assistant d'E-mail IA !",
        "Select your language": "Sélectionnez votre langue",
        "Generate Email": "Générer l'e-mail",
        "Compose your email details below.": "Composez les détails de votre e-mail ci-dessous.",
        "Recipient": "Destinataire",
        "Subject": "Objet",
        "Body": "Corps du message",
        "Sender": "Expéditeur",
        "Clear Form": "Effacer le formulaire",
        "Your email has been generated!": "Votre e-mail a été généré !",
        "Error generating email. Please try again.": "Erreur lors de la génération de l'e-mail. Veuillez réessayer.",
        "Recipient, Subject, and Body cannot be empty.": "Le destinataire, l'objet et le corps du message ne peuvent pas être vides.",
        "Enter a recipient": "Saisissez un destinataire",
        "Enter a subject": "Saisissez un objet",
        "Enter email body": "Saisissez le corps de l'e-mail",
        "Enter sender name or email": "Saisissez le nom ou l'e-mail de l'expéditeur",
        # New Translations
        "1. Email Generation": "1. Génération de l'e-mail",
        "Upload an Excel file with contacts (.xlsx)": "Importer un fichier Excel avec les contacts (.xlsx)",
        "Successfully loaded {count} valid contacts.": "{count} contacts valides ont été chargés avec succès.",
        "WARNING: Some contacts had issues (e.g., missing/invalid/duplicate emails). They will be skipped.": "ATTENTION : Certains contacts présentaient des problèmes (par exemple, e-mails manquants/invalides/dupliqués). Ils seront ignorés.",
        "Show Contact Issues": "Afficher les problèmes de contact",
        "No valid contacts loaded. Please check the issues below.": "Aucun contact valide n'a été chargé. Veuillez vérifier les problèmes ci-dessous.",
        "No contacts found in the uploaded file or file was empty.": "Aucun contact trouvé dans le fichier téléchargé ou le fichier était vide.",
        "What kind of email do you want to generate?": "Quel type d'e-mail souhaitez-vous générer ?",
        "e.g., 'A welcome email for new customers, offering a 10% discount.'": "ex: 'Un e-mail de bienvenue pour les nouveaux clients, offrant une réduction de 10 %.'",
        "Any specific style, tone, or information to include?": "Un style, un ton ou des informations spécifiques à inclure ?",
        "e.g., 'Formal tone, mention our website: example.com. Use placeholders for Name and Email.'": "ex: 'Ton formel, mentionnez notre site web: example.com. Utilisez des espaces réservés pour Nom et E-mail.'",
        "Attach files (optional)": "Joindre des fichiers (facultatif)",
        "Drag and drop files here": "Faites glisser et déposez les fichiers ici",
        "Currently attached files:": "Fichiers actuellement joints :",
        "Remove": "Supprimer",
        "Clear All Attachments": "Effacer toutes les pièces jointes",
        "Personalize emails for each recipient (replaces {{Name}}, {{Email}})": "Personnaliser les e-mails pour chaque destinataire (remplace {{Name}}, {{Email}})",
        "Proceed to Review & Send": "Passer à la révision et à l'envoi",
        "Subject and Body cannot be empty to proceed.": "L'objet et le corps du message ne peuvent pas être vides pour continuer.",
        "2. Review & Send": "2. Révision et Envoi",
        "Review your email content and contacts before sending.": "Vérifiez le contenu de votre e-mail et vos contacts avant l'envoi.",
        "Email Preview (First Contact)": "Aperçu de l'e-mail (premier contact)",
        "No contacts loaded to show a preview.": "Aucun contact chargé pour afficher un aperçu.",
        "Attached Files": "Fichiers joints",
        "Contacts Overview": "Aperçu des contacts",
        "{count} valid contacts loaded.": "{count} contacts valides chargés.",
        "Back to Edit Email": "Retour à la modification de l'e-mail",
        "Send All Emails": "Envoyer tous les e-mails",
        "3. Results": "3. Résultats",
        "Start New Email Session": "Commencer une nouvelle session d'e-mail",
        "All emails sent successfully!": "Tous les e-mails ont été envoyés avec succès !",
        "All {count} emails were sent without any issues.": "Les {count} e-mails ont été envoyés sans aucun problème.",
        "Sending complete with errors.": "Envoi terminé avec des erreurs.",
        "Some emails failed to send. Please check the log below for details.": "Certains e-mails n'ont pas pu être envoyés. Veuillez consulter le journal ci-dessous pour plus de détails.",
        "No emails were sent. Please upload contacts and generate an email first.": "Aucun e-mail n'a été envoyé. Veuillez d'abord télécharger des contacts et générer un e-mail.",
        "Total Contacts": "Total des contacts",
        "Emails Successfully Sent": "E-mails envoyés avec succès",
        "Emails Failed to Send": "E-mails échoués",
        "Show Activity Log and Errors": "Afficher le journal d'activité et les erreurs",
        "Download Failed Emails Log": "Télécharger le journal des e-mails échoués",
        "Settings": "Paramètres",
        "This tool helps you generate and send personalized emails efficiently.": "Cet outil vous aide à générer et envoyer des e-mails personnalisés efficacement.",
        "Sender Email: {email} (Configured in secrets)": "E-mail de l'expéditeur : {email} (Configuré dans les secrets)",
        "Sender email is not configured. Please set SENDER_EMAIL and SENDER_PASSWORD in your Streamlit secrets.": "L'e-mail de l'expéditeur n'est pas configuré. Veuillez définir SENDER_EMAIL et SENDER_PASSWORD dans vos secrets Streamlit.",
        "Drag and drop file here": "Faites glisser et déposez le fichier ici",
        "Please provide a prompt to generate the email.": "Veuillez fournir une instruction pour générer l'e-mail.",
        "Generating email content...": "Génération du contenu de l'e-mail...",
        "Email content generated successfully.": "Contenu de l'e-mail généré avec succès.",
        "Error generating email: {error_message}": "Erreur lors de la génération de l'e-mail : {error_message}",
        "No contacts loaded. Please upload a contact list first.": "Aucun contact chargé. Veuillez d'abord télécharger une liste de contacts.",
        "Email subject or body is empty. Please generate email content first.": "L'objet ou le corps de l'e-mail est vide. Veuillez d'abord générer le contenu de l'e-mail.",
        "Email sending process initiated...": "Processus d'envoi d'e-mails initié...",
        "Temporary directory created for attachments: {temp_dir}": "Répertoire temporaire créé pour les pièces jointes : {temp_dir}",
        "Skipping invalid attachment: {attachment_path}": "Sauter la pièce jointe invalide : {attachment_path}",
        "Skipping contact {name} due to missing email.": "Sauter le contact {name} en raison d'un e-mail manquant.",
        "--- [{current_num}/{total_num}] Processing contact: {name} ({email}) ---": "--- [{current_num}/{total_num}] Traitement du contact : {name} ({email}) ---",
        "Generating personalized email for {name}...": "Génération de l'e-mail personnalisé pour {name}...",
        "Error personalizing email for {name}: {error_message}": "Erreur lors de la personnalisation de l'e-mail pour {name} : {error_message}",
        "Attempting Email for {name}...": "Tentative d'envoi d'e-mail pour {name}...",
        "Email sent to {recipient_email} successfully.": "E-mail envoyé à {recipient_email} avec succès.",
        "Failed to send to {recipient_email}. Details: {message}": "Échec de l'envoi à {recipient_email}. Détails : {message}",
        "An unexpected error occurred during email sending: {error_message}": "Une erreur inattendue est survenue lors de l'envoi de l'e-mail : {error_message}",
        "--- Email sending process complete ---": "--- Processus d'envoi d'e-mails terminé ---",
        "Summary: {successful_count} successful, {failed_count} failed/skipped.": "Résumé : {successful_count} réussis, {failed_count} échoués/ignorés.",
        "Temporary directory deleted: {temp_dir}": "Répertoire temporaire supprimé : {temp_dir}",
        "Error deleting temporary directory {temp_dir}: {error_message}": "Erreur lors de la suppression du répertoire temporaire {temp_dir} : {error_message}",
        "Configuration Error: {error_message}. Please ensure OPENAI_API_KEY is set in your Streamlit secrets.": "Erreur de configuration : {error_message}. Veuillez vous assurer que OPENAI_API_KEY est défini dans vos secrets Streamlit.",
        "Session state cleared.": "État de la session effacé.",
        "Temporary Excel file deleted: {file_path}": "Fichier Excel temporaire supprimé : {file_path}",
        "Error deleting temporary Excel file {file_path}: {error_message}": "Erreur lors de la suppression du fichier Excel temporaire {file_path} : {error_message}",
        "Contact {index}": "Contact {index}"
    }
}

# Default language if no session state is set
DEFAULT_LANG = "en"

# Global variable to store the selected language
_selected_lang = DEFAULT_LANG

def set_language(lang_code):
    """Sets the global language for translations."""
    global _selected_lang
    if lang_code in LANGUAGES:
        _selected_lang = lang_code
    else:
        _selected_lang = DEFAULT_LANG # Fallback to default if invalid code

def _t(key, **kwargs):
    """
    Translates a given key into the selected language and formats it with kwargs.
    If the key is not found, it returns the key itself as a fallback.
    """
    translation_dict = TRANSLATIONS.get(_selected_lang, {})
    translated_string = translation_dict.get(key, key) # Fallback to key if not found
    
    # Apply formatting with kwargs
    try:
        return translated_string.format(**kwargs)
    except KeyError as e:
        # This means a placeholder in the translated string (or original key if not translated)
        # was not provided in kwargs.
        return f"Formatting Error: Missing key '{e.args[0]}'"
    except Exception as e:
        # Catch any other formatting errors
        return f"Formatting Error: {e}"