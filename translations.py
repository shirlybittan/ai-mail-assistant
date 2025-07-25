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
        "No contacts loaded or file is empty/invalid.": "No contacts loaded or file is empty/invalid.",
        "Issue(s) encountered:": "Issue(s) encountered:",
        "Successfully uploaded: {file_name}": "Successfully uploaded: {file_name}",
        "Select Contacts": "Select Contacts",
        "Email Generation Prompt": "Email Generation Prompt",
        "Enter your prompt for the AI to generate the email template.": "Enter your prompt for the AI to generate the email template.",
        "Generate Email Template": "Generate Email Template",
        "Email Content Preview": "Email Content Preview",
        "Subject:": "Subject:",
        "Body:": "Body:",
        "Preview Email": "Preview Email",
        "Send Emails": "Send Emails",
        "Personalized Emails": "Personalized Emails",
        "If checked, emails will be personalized for each contact (e.g., Hi {Name}). Otherwise, a generic template will be used.": "If checked, emails will be personalized for each contact (e.g., Hi {Name}). Otherwise, a generic template will be used.",
        "No email template generated yet.": "No email template generated yet.",
        "Total Contacts Loaded": "Total Contacts Loaded",
        "2. Email Preview & Send": "2. Email Preview & Send",
        "Confirm Send": "Confirm Send",
        "3. Results": "3. Results",
        "Start New Email Session": "Start New Email Session",
        "Total": "Total",
        "Success": "Success",
        "Failed": "Failed",
        "Activity Log": "Activity Log",
        "Back to Generate Email": "Back to Generate Email", # New translation
        "All emails sent successfully!": "All emails sent successfully!",
        "All {count} emails were sent without any issues.": "All {count} emails were sent without any issues.",
        "Sending complete with errors.": "Sending complete with errors.",
        "Some emails failed to send. Please check the log below for details.": "Some emails failed to send. Please check the log below for details.",
        "Summary": "Summary",
        "Total Contacts": "Total Contacts",
        "Emails Successfully Sent": "Emails Successfully Sent",
        "Emails Failed to Send": "Emails Failed to Send",
        "Show Activity Log and Errors": "Show Activity Log and Errors",
        "No contacts available to send emails. Please upload contacts first.": "No contacts available to send emails. Please upload contacts first.",
        "No email content to send. Please generate an email template first.": "No email content to send. Please generate an email template first.",
        "Email sending process initiated...": "Email sending process initiated...",
        "Sending emails...": "Sending emails...",
        "Email preview generated successfully.": "Email preview generated successfully.",
        "Generating email preview for the first contact. This may take a moment...": "Generating email preview for the first contact. This may take a moment...",
        "Using first contact for preview: {name}": "Using first contact for preview: {name}",
        "Generating personalized email for {name}...": "Generating personalized email for {name}...",
        "Attempting Email for {name}...": "Attempting Email for {name}...",
        "    - Email: success - Email sent to {email} successfully.": "    - Email: success - Email sent to {email} successfully.",
        "    - Email: error - Failed to send to {email}. Details: {message}": "    - Email: error - Failed to send to {email}. Details: {message}",
        "    - Email: error - An unexpected error occurred for {email}: {error}": "    - Email: error - An unexpected error occurred for {email}: {error}",
        "--- Email sending process complete ---": "--- Email sending process complete ---",
        "Summary: {successful} successful, {failed} failed/skipped.": "Summary: {successful} successful, {failed} failed/skipped.",
        "Email generated with generic placeholders (e.g., {{Name}}, {{Email}}) as personalization is off.": "Email generated with generic placeholders (e.g., {{Name}}, {{Email}}) as personalization is off.",
        "The generated email template includes placeholders. To see the actual personalized content, please ensure 'Personalized Emails' is checked.": "The generated email template includes placeholders. To see the actual personalized content, please ensure 'Personalized Emails' is checked.",
        "Placeholder Info": "Placeholder Info",
        "Template Preview (with placeholders if personalization is off)": "Template Preview (with placeholders if personalization is off)",
        "Email sending process initiated...": "Email sending process initiated...",
        "Email sending process complete.": "Email sending process complete.",
        "Finished sending emails.": "Finished sending emails.",
        "Successfully sent: {successful}": "Successfully sent: {successful}",
        "Failed/Skipped: {failed}": "Failed/Skipped: {failed}",
        "Check the Activity Log and 'failed_emails_log.txt' for details.": "Check the Activity Log and 'failed_emails_log.txt' for details.",
        "Sending complete with issues.": "Sending complete with issues.",
        "Email sending in progress. Please wait...": "Email sending in progress. Please wait...",
        "Current Language: {lang}": "Current Language: {lang}",
    },
    "fr": {
        "AI Email Assistant": "Assistant d'e-mails IA",
        "Welcome to the AI Email Assistant!": "Bienvenue dans l'assistant d'e-mails IA !",
        "Select your language": "Sélectionnez votre langue",
        "Generate Email": "Générer un e-mail",
        "Compose your email details below.": "Composez les détails de votre e-mail ci-dessous.",
        "Recipient": "Destinataire",
        "Subject": "Objet",
        "Body": "Corps",
        "Sender": "Expéditeur",
        "Clear Form": "Effacer le formulaire",
        "Your email has been generated!": "Votre e-mail a été généré !",
        "Error generating email. Please try again.": "Erreur lors de la génération de l'e-mail. Veuillez réessayer.",
        "Recipient, Subject, and Body cannot be empty.": "Le destinataire, l'objet et le corps ne peuvent pas être vides.",
        "Enter a recipient": "Entrez un destinataire",
        "Enter a subject": "Entrez un objet",
        "Enter email body": "Entrez le corps de l'e-mail",
        "Enter sender name or email": "Entrez le nom ou l'e-mail de l'expéditeur",
        # New Translations
        "1. Email Generation": "1. Génération d'e-mails",
        "Upload an Excel file with contacts (.xlsx)": "Importer un fichier Excel avec les contacts (.xlsx)",
        "Successfully loaded {count} valid contacts.": "{count} contacts valides ont été chargés avec succès.",
        "No contacts loaded or file is empty/invalid.": "Aucun contact chargé ou le fichier est vide/invalide.",
        "Issue(s) encountered:": "Problème(s) rencontré(s) :",
        "Successfully uploaded: {file_name}": "Importé avec succès : {file_name}",
        "Select Contacts": "Sélectionner les contacts",
        "Email Generation Prompt": "Invite de génération d'e-mail",
        "Enter your prompt for the AI to generate the email template.": "Entrez votre invite pour que l'IA génère le modèle d'e-mail.",
        "Generate Email Template": "Générer le modèle d'e-mail",
        "Email Content Preview": "Aperçu du contenu de l'e-mail",
        "Subject:": "Objet :",
        "Body:": "Corps :",
        "Preview Email": "Aperçu de l'e-mail",
        "Send Emails": "Envoyer les e-mails",
        "Personalized Emails": "E-mails personnalisés",
        "If checked, emails will be personalized for each contact (e.g., Bonjour {Nom}). Sinon, un modèle générique sera utilisé.": "Si cette option est cochée, les e-mails seront personnalisés pour chaque contact (par exemple, Bonjour {Nom}). Sinon, un modèle générique sera utilisé.",
        "No email template generated yet.": "Aucun modèle d'e-mail généré pour l'instant.",
        "Total Contacts Loaded": "Total des contacts chargés",
        "2. Email Preview & Send": "2. Aperçu et envoi d'e-mails",
        "Confirm Send": "Confirmer l'envoi",
        "3. Results": "3. Résultats",
        "Start New Email Session": "Démarrer une nouvelle session d'e-mails",
        "Total": "Total",
        "Success": "Succès",
        "Failed": "Échoué",
        "Activity Log": "Journal d'activité",
        "Back to Generate Email": "Retour à la génération d'e-mails", # New translation
        "All emails sent successfully!": "Tous les e-mails ont été envoyés avec succès !",
        "All {count} emails were sent without any issues.": "Les {count} e-mails ont été envoyés sans aucun problème.",
        "Sending complete with errors.": "Envoi terminé avec des erreurs.",
        "Some emails failed to send. Please check the log below for details.": "Certains e-mails n'ont pas pu être envoyés. Veuillez consulter le journal ci-dessous pour plus de détails.",
        "Summary": "Résumé",
        "Total Contacts": "Total des contacts",
        "Emails Successfully Sent": "E-mails envoyés avec succès",
        "Emails Failed to Send": "E-mails échoués",
        "Show Activity Log and Errors": "Afficher le journal d'activité et les erreurs",
        "No contacts available to send emails. Please upload contacts first.": "Aucun contact disponible pour envoyer des e-mails. Veuillez d'abord importer des contacts.",
        "No email content to send. Please generate an email template first.": "Aucun contenu d'e-mail à envoyer. Veuillez d'abord générer un modèle d'e-mail.",
        "Email sending process initiated...": "Processus d'envoi d'e-mails initié...",
        "Sending emails...": "Envoi d'e-mails...",
        "Email preview generated successfully.": "Aperçu de l'e-mail généré avec succès.",
        "Generating email preview for the first contact. This may take a moment...": "Génération de l'aperçu de l'e-mail pour le premier contact. Cela peut prendre un moment...",
        "Using first contact for preview: {name}": "Utilisation du premier contact pour l'aperçu : {name}",
        "Generating personalized email for {name}...": "Génération d'un e-mail personnalisé pour {name}...",
        "Attempting Email for {name}...": "Tentative d'envoi d'e-mail pour {name}...",
        "    - Email: success - Email sent to {email} successfully.": "    - E-mail : succès - E-mail envoyé à {email} avec succès.",
        "    - Email: error - Failed to send to {email}. Details: {message}": "    - E-mail : erreur - Échec de l'envoi à {email}. Détails : {message}",
        "    - Email: error - An unexpected error occurred for {email}: {error}": "    - E-mail : erreur - Une erreur inattendue est survenue pour {email} : {error}",
        "--- Email sending process complete ---": "--- Processus d'envoi d'e-mails terminé ---",
        "Summary: {successful} successful, {failed} failed/skipped.": "Résumé : {successful} succès, {failed} échecs/ignorés.",
        "Email generated with generic placeholders (e.g., {{Name}}, {{Email}}) as personalization is off.": "E-mail généré avec des espaces réservés génériques (par exemple, {{Name}}, {{Email}}) car la personnalisation est désactivée.",
        "The generated email template includes placeholders. To see the actual personalized content, please ensure 'Personalized Emails' is checked.": "Le modèle d'e-mail généré inclut des espaces réservés. Pour voir le contenu personnalisé réel, veuillez vous assurer que la case 'E-mails personnalisés' est cochée.",
        "Placeholder Info": "Infos sur les espaces réservés",
        "Template Preview (with placeholders if personalization is off)": "Aperçu du modèle (avec des espaces réservés si la personnalisation est désactivée)",
        "Email sending process initiated...": "Processus d'envoi d'e-mails initié...",
        "Email sending process complete.": "Processus d'envoi d'e-mails terminé.",
        "Finished sending emails.": "Envoi d'e-mails terminé.",
        "Successfully sent: {successful}": "Envoyé avec succès : {successful}",
        "Failed/Skipped: {failed}": "Échoué/Ignoré : {failed}",
        "Check the Activity Log and 'failed_emails_log.txt' for details.": "Vérifiez le journal d'activité et 'failed_emails_log.txt' pour plus de détails.",
        "Sending complete with issues.": "Envoi terminé avec des problèmes.",
        "Email sending in progress. Please wait...": "Envoi d'e-mails en cours. Veuillez patienter...",
        "Current Language: {lang}": "Langue actuelle : {lang}",
    }
}

# Default language if no session state is set
DEFAULT_LANG = "en"

# Global variable to store the selected language
# This will now be directly controlled by Streamlit's session_state in streamlit_app.py
# No need for a global variable here if it's handled by session_state.

def set_language(lang_code):
    """Sets the language for translations by updating Streamlit's session state."""
    # This function is now mostly illustrative; the actual language setting
    # and retrieval should happen directly from st.session_state in streamlit_app.py
    # and this function should ideally be removed or modified to accept session_state
    # if it's strictly needed. For now, we'll keep it but rely on app.py for state.
    pass # The logic for setting language is moved to streamlit_app.py for session state persistence.

def _t(key, **kwargs):
    """
    Translates a given key into the selected language and formats it with kwargs.
    It now directly accesses st.session_state for the language.
    If the key is not found, it returns the key itself as a fallback.
    """
    import streamlit as st # Import st inside the function to avoid circular dependency if translations is imported by st.app
    current_lang = st.session_state.get('language', DEFAULT_LANG) # Get language from session state
    
    translation_dict = TRANSLATIONS.get(current_lang, TRANSLATIONS[DEFAULT_LANG])
    translated_text = translation_dict.get(key, key) # Fallback to key if translation not found
    
    # Format the translated text with keyword arguments
    try:
        return translated_text.format(**kwargs)
    except KeyError as e:
        # Handle cases where placeholders in translation are missing in kwargs
        return f"{translated_text} (Formatting Error: Missing key {e})"
    except IndexError as e:
        # Handle cases where positional arguments are expected but not given
        return f"{translated_text} (Formatting Error: Positional arg issue {e})"