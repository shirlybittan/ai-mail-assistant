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
        "Error loading contacts: {error_message}": "Error loading contacts: {error_message}",
        "2. Email Preview & Send": "2. Email Preview & Send",
        "No contacts loaded yet. Please go back to Email Generation to upload a file.": "No contacts loaded yet. Please go back to Email Generation to upload a file.",
        "Customize emails for each recipient (replaces {{Name}}, {{Email}})": "Customize emails for each recipient (replaces {{Name}}, {{Email}})",
        "Generic Greeting Placeholder (e.g., 'Dear {{Name}}' or 'Hello')": "Generic Greeting Placeholder (e.g., 'Dear {{Name}}' or 'Hello')",
        "Email Preview": "Email Preview",
        "Generating email preview for the first contact. This may take a moment...": "Generating email preview for the first contact. This may take a moment...",
        "Using first contact for preview: {name} ({email})": "Using first contact for preview: {name} ({email})",
        "Email preview generated successfully.": "Email preview generated successfully.",
        "No email preview available. Generate an email and load contacts first.": "No email preview available. Generate an email and load contacts first.",
        "Confirm Send": "Confirm Send",
        "Sending emails...": "Sending emails...",
        "Email sending process initiated...": "Email sending process initiated...",
        "--- [{current}/{total}] Processing contact: {name} ({email}) ---": "--- [{current}/{total}] Processing contact: {name} ({email}) ---",
        "Generating personalized email for {name}...": "Generating personalized email for {name}...",
        "Attempting Email for {name}...": "Attempting Email for {name}...",
        "    - Email: success - Email sent to {email} successfully.": "    - Email: success - Email sent to {email} successfully.",
        "    - Email: error - Failed to send to {email}. Details: {message}": "    - Email: error - Failed to send to {email}. Details: {message}",
        "    - Email: error - An unexpected error occurred for {email}: {error}": "    - Email: error - An unexpected error occurred for {email}: {error}",
        "--- Email sending process complete ---": "--- Email sending process complete ---",
        "Summary: {successful} successful, {failed} failed/skipped.": "Summary: {successful} successful, {failed} failed/skipped.",
        "Finished sending emails.": "Finished sending emails.",
        "Successful": "Successful",
        "Failed/Skipped": "Failed/Skipped",
        "Check the Activity Log and 'failed_emails_log.txt' for details.": "Check the Activity Log and 'failed_emails_log.txt' for details.",
        "3. Results": "3. Results",
        "Start New Email Session": "Start New Email Session",
        "Total": "Total",
        "Success": "Success",
        "Failed": "Failed",
        "Activity Log": "Activity Log",
        "Language": "Language",
        "Your email has been generated! You can edit it below.": "Votre e-mail a été généré ! Vous pouvez le modifier ci-dessous.",
        "Welcome! Use the sidebar to navigate.": "Bienvenue ! Utilisez la barre latérale pour naviguer.",
        "All emails sent successfully!": "Tous les e-mails ont été envoyés avec succès !",
        "All {count} emails were sent without any issues.": "Les {count} e-mails ont été envoyés sans aucun problème.",
        "Sending complete with errors.": "Envoi terminé avec des erreurs.",
        "Some emails failed to send. Please check the log below for details.": "Certains e-mails n'ont pas pu être envoyés. Veuillez consulter le journal ci-dessous pour plus de détails.",
        "Summary": "Résumé",
        "Total Contacts": "Total des contacts",
        "Emails Successfully Sent": "E-mails envoyés avec succès",
        "Emails Failed to Send": "E-mails échoués",
        "Show Activity Log and Errors": "Afficher le journal d'activité et les erreurs"
    },
    "fr": {
        "AI Email Assistant": "Assistant d'e-mail IA",
        "Welcome to the AI Email Assistant!": "Bienvenue dans l'Assistant d'e-mail IA !",
        "Select your language": "Sélectionnez votre langue",
        "Generate Email": "Générer un e-mail",
        "Compose your email details below.": "Composez les détails de votre e-mail ci-dessous.",
        "Recipient": "Destinataire",
        "Subject": "Objet",
        "Body": "Corps du message",
        "Sender": "Expéditeur",
        "Clear Form": "Effacer le formulaire",
        "Your email has been generated!": "Votre e-mail a été généré !",
        "Error generating email. Please try again.": "Erreur lors de la génération de l'e-mail. Veuillez réessayer.",
        "Recipient, Subject, and Body cannot be empty.": "Destinataire, objet et corps du message ne peuvent pas être vides.",
        "Enter a recipient": "Saisissez un destinataire",
        "Enter a subject": "Saisissez un objet",
        "Enter email body": "Saisissez le corps de l'e-mail",
        "Enter sender name or email": "Saisissez le nom ou l'e-mail de l'expéditeur",
        # New Translations
        "1. Email Generation": "1. Génération d'e-mails",
        "Upload an Excel file with contacts (.xlsx)": "Importer un fichier Excel avec les contacts (.xlsx)",
        "Successfully loaded {count} valid contacts.": "Chargement réussi de {count} contacts valides.",
        "WARNING: Some contacts had issues (e.g., missing/invalid/duplicate emails). They will be skipped.": "ATTENTION : Certains contacts ont eu des problèmes (ex. : e-mails manquants/invalides/dupliqués). Ils seront ignorés.",
        "Error loading contacts: {error_message}": "Erreur lors du chargement des contacts : {error_message}",
        "2. Email Preview & Send": "2. Aperçu et envoi de l'e-mail",
        "No contacts loaded yet. Please go back to Email Generation to upload a file.": "Aucun contact chargé pour l'instant. Veuillez retourner à la génération d'e-mails pour télécharger un fichier.",
        "Customize emails for each recipient (replaces {{Name}}, {{Email}})": "Personnaliser les e-mails pour chaque destinataire (remplace {{Name}}, {{Email}})",
        "Generic Greeting Placeholder (e.g., 'Dear {{Name}}' or 'Hello')": "Texte générique de salutation (ex. : 'Cher {{Name}}' ou 'Bonjour')",
        "Email Preview": "Aperçu de l'e-mail",
        "Generating email preview for the first contact. This may take a moment...": "Génération de l'aperçu de l'e-mail pour le premier contact. Cela peut prendre un instant...",
        "Using first contact for preview: {name} ({email})": "Utilisation du premier contact pour l'aperçu : {name} ({email})",
        "Email preview generated successfully.": "Aperçu de l'e-mail généré avec succès.",
        "No email preview available. Generate an email and load contacts first.": "Aucun aperçu d'e-mail disponible. Générez un e-mail et chargez d'abord les contacts.",
        "Confirm Send": "Confirmer l'envoi",
        "Sending emails...": "Envoi des e-mails...",
        "Email sending process initiated...": "Processus d'envoi d'e-mails initié...",
        "--- [{current}/{total}] Processing contact: {name} ({email}) ---": "--- [{current}/{total}] Traitement du contact : {name} ({email}) ---",
        "Generating personalized email for {name}...": "Génération d'un e-mail personnalisé pour {name}...",
        "Attempting Email for {name}...": "Tentative d'envoi d'e-mail pour {name}...",
        "    - Email: success - Email sent to {email} successfully.": "    - E-mail : succès - E-mail envoyé à {email} avec succès.",
        "    - Email: error - Failed to send to {email}. Details: {message}": "    - E-mail : erreur - Échec de l'envoi à {email}. Détails : {message}",
        "    - Email: error - An unexpected error occurred for {email}: {error}": "    - E-mail : erreur - Une erreur inattendue est survenue pour {email} : {error}",
        "--- Email sending process complete ---": "--- Processus d'envoi d'e-mails terminé ---",
        "Summary: {successful} successful, {failed} failed/skipped.": "Résumé : {successful} réussis, {failed} échoués/ignorés.",
        "Finished sending emails.": "Envoi des e-mails terminé.",
        "Successful": "Réussis",
        "Failed/Skipped": "Échoués/Ignorés",
        "Check the Activity Log and 'failed_emails_log.txt' for details.": "Consultez le journal d'activité et 'failed_emails_log.txt' pour les détails.",
        "3. Results": "3. Résultats",
        "Start New Email Session": "Démarrer une nouvelle session d'e-mails",
        "Total": "Total",
        "Success": "Succès",
        "Failed": "Échoué",
        "Activity Log": "Journal d'activité",
        "Language": "Langue",
        "Your email has been generated! You can edit it below.": "Votre e-mail a été généré ! Vous pouvez le modifier ci-dessous.",
        "Welcome! Use the sidebar to navigate.": "Bienvenue ! Utilisez la barre latérale pour naviguer.",
        "All emails sent successfully!": "Tous les e-mails ont été envoyés avec succès !",
        "All {count} emails were sent without any issues.": "Les {count} e-mails ont été envoyés sans aucun problème.",
        "Sending complete with errors.": "Envoi terminé avec des erreurs.",
        "Some emails failed to send. Please check the log below for details.": "Certains e-mails n'ont pas pu être envoyés. Veuillez consulter le journal ci-dessous pour plus de détails.",
        "Summary": "Résumé",
        "Total Contacts": "Total des contacts",
        "Emails Successfully Sent": "E-mails envoyés avec succès",
        "Emails Failed to Send": "E-mails échoués",
        "Show Activity Log and Errors": "Afficher le journal d'activité et les erreurs"
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
    translated_string = TRANSLATIONS.get(_selected_lang, {}).get(key, key)
    try:
        return translated_string.format(**kwargs)
    except KeyError:
        return translated_string # Return without formatting if kwargs don't match