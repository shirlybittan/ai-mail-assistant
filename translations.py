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
        "Settings": "Settings",
        "Select your language": "Select your language",
        "This app allows you to send mass personalized emails using an AI agent.": "This app allows you to send mass personalized emails using an AI agent.",
        "1. Email Generation": "1. Email Generation",
        "Upload an Excel file with contacts (.xlsx)": "Upload an Excel file with contacts (.xlsx)",
        "Successfully loaded {count} valid contacts.": "Successfully loaded {count} valid contacts.",
        "Some contacts had issues and were skipped.": "Some contacts had issues and were skipped.",
        "Show skipped contacts": "Show skipped contacts",
        "Using previously loaded contacts: {count} valid contacts found.": "Using previously loaded contacts: {count} valid contacts found.",
        "Personalize emails for each contact?": "Personalize emails for each contact?",
        "Generic Greeting Placeholder (e.g., 'Dear Friends')": "Generic Greeting Placeholder (e.g., 'Dear Friends')",
        "Enter your instruction for the AI agent:": "Enter your instruction for the AI agent:",
        "AI Instruction": "AI Instruction",
        "e.g., 'Write a follow-up email to customers who purchased our new product. Thank them and offer a discount on their next purchase.'": "e.g., 'Write a follow-up email to customers who purchased our new product. Thank them and offer a discount on their next purchase.'",
        "Additional context for the email (optional):": "Additional context for the email (optional):",
        "Email Context": "Email Context",
        "e.g., 'Keep the tone professional but friendly.'": "e.g., 'Keep the tone professional but friendly.'",
        "Attachments (Optional)": "Attachments (Optional)",
        "Upload files to attach to all emails": "Upload files to attach to all emails",
        "You have uploaded {count} attachments.": "You have uploaded {count} attachments.",
        "Generate Previews": "Generate Previews",
        "2. Review and Send Emails": "2. Review and Send Emails",
        "Review the generated email template below. You can edit the subject and body before sending.": "Review the generated email template below. You can edit the subject and body before sending.",
        "Email Preview": "Email Preview",
        "Activity Log": "Activity Log",
        "Subject": "Subject",
        "Body": "Body",
        "Send All Emails": "Send All Emails",
        "Start New Email Session": "Start New Email Session",
        "Generating email template... This may take a moment.": "Generating email template... This may take a moment.",
        "  - Generated template email successfully.": "  - Generated template email successfully.",
        "  - ERROR: Failed to generate template email. Details: {details}": "  - ERROR: Failed to generate template email. Details: {details}",
        "--- [1/4] Processing contact: bittanshirly Smith (bittanshirly@gmail.com) ---": "--- [1/4] Processing contact: bittanshirly Smith (bittanshirly@gmail.com) ---",
        "Email sending process initiated...": "Email sending process initiated...",
        "--- [{current}/{total}] Processing contact: {name} ({email}) ---": "--- [{current}/{total}] Processing contact: {name} ({email}) ---",
        "  Attempting Email for {name}...": "  Attempting Email for {name}...",
        "    - Email: success - Email sent to {email} successfully.": "    - Email: success - Email sent to {email} successfully.",
        "    - Email: error - Failed to send to {email}. Details: {details}": "    - Email: error - Failed to send to {email}. Details: {details}",
        "--- Email sending process complete ---": "--- Email sending process complete ---",
        "ERROR: Could not clean up temporary attachments: ": "ERROR: Could not clean up temporary attachments: ",
        "3. Sending Results": "3. Sending Results",
        "Email sending is complete!": "Email sending is complete!",
        "Total Emails Sent": "Total Emails Sent",
        "Emails Successfully Sent": "Emails Successfully Sent",
        "Emails Failed to Send": "Emails Failed to Send",
        "A detailed log has been recorded below.": "A detailed log has been recorded below.",
        "Generation Log": "Generation Log",
        # New strings for the results page
        "Sending complete": "Sending complete",
        "All emails have been sent or an attempt has been made for each contact.": "All emails have been sent or an attempt has been made for each contact.",
        "Sending Log": "Sending Log",
        "Total Contacts": "Total Contacts",
        "This app has encountered an error.": "This app has encountered an error.",
    },
    "fr": {
        "AI Email Assistant": "Assistant d'E-mail IA",
        "Settings": "Paramètres",
        "Select your language": "Sélectionnez votre langue",
        "This app allows you to send mass personalized emails using an AI agent.": "Cette application vous permet d'envoyer des e-mails personnalisés en masse à l'aide d'un agent IA.",
        "1. Email Generation": "1. Génération d'E-mail",
        "Upload an Excel file with contacts (.xlsx)": "Télécharger un fichier Excel avec des contacts (.xlsx)",
        "Successfully loaded {count} valid contacts.": "Chargement réussi de {count} contacts valides.",
        "Some contacts had issues and were skipped.": "Certains contacts avaient des problèmes et ont été ignorés.",
        "Show skipped contacts": "Afficher les contacts ignorés",
        "Using previously loaded contacts: {count} valid contacts found.": "Utilisation des contacts précédemment chargés : {count} contacts valides trouvés.",
        "Personalize emails for each contact?": "Personnaliser les e-mails pour chaque contact ?",
        "Generic Greeting Placeholder (e.g., 'Dear Friends')": "Texte d'accueil générique (par exemple, 'Chers amis')",
        "Enter your instruction for the AI agent:": "Entrez vos instructions pour l'agent IA :",
        "AI Instruction": "Instruction IA",
        "e.g., 'Write a follow-up email to customers who purchased our new product. Thank them and offer a discount on their next purchase.'": "ex., 'Rédigez un e-mail de suivi aux clients qui ont acheté notre nouveau produit. Remerciez-les et offrez-leur une réduction sur leur prochain achat.'",
        "Additional context for the email (optional):": "Contexte supplémentaire pour l'e-mail (facultatif) :",
        "Email Context": "Contexte de l'e-mail",
        "e.g., 'Keep the tone professional but friendly.'": "ex., 'Gardez un ton professionnel mais amical.'",
        "Attachments (Optional)": "Pièces jointes (facultatif)",
        "Upload files to attach to all emails": "Télécharger des fichiers à joindre à tous les e-mails",
        "You have uploaded {count} attachments.": "Vous avez téléchargé {count} pièces jointes.",
        "Generate Previews": "Générer les aperçus",
        "2. Review and Send Emails": "2. Vérifier et envoyer les e-mails",
        "Review the generated email template below. You can edit the subject and body before sending.": "Vérifiez le modèle d'e-mail généré ci-dessous. Vous pouvez modifier l'objet et le corps avant d'envoyer.",
        "Email Preview": "Aperçu de l'e-mail",
        "Activity Log": "Journal d'activité",
        "Subject": "Objet",
        "Body": "Corps",
        "Send All Emails": "Envoyer tous les e-mails",
        "Start New Email Session": "Démarrer une nouvelle session d'e-mail",
        "Generating email template... This may take a moment.": "Génération du modèle d'e-mail... Cela peut prendre un instant.",
        "  - Generated template email successfully.": "  - Modèle d'e-mail généré avec succès.",
        "  - ERROR: Failed to generate template email. Details: {details}": "  - ERREUR : Échec de la génération du modèle d'e-mail. Détails : {details}",
        "--- [{current}/{total}] Processing contact: {name} ({email}) ---": "--- [{current}/{total}] Traitement du contact : {name} ({email}) ---",
        "  Attempting Email for {name}...": "  Tentative d'envoi pour {name}...",
        "    - Email: success - Email sent to {email} successfully.": "    - E-mail : succès - E-mail envoyé à {email} avec succès.",
        "    - Email: error - Failed to send to {email}. Details: {details}": "    - E-mail : erreur - Échec de l'envoi à {email}. Détails : {details}",
        "--- Email sending process complete ---": "--- Processus d'envoi d'e-mails terminé ---",
        "ERROR: Could not clean up temporary attachments: ": "ERREUR : Impossible de nettoyer les pièces jointes temporaires : ",
        "3. Sending Results": "3. Résultats d'envoi",
        "Email sending is complete!": "L'envoi des e-mails est terminé !",
        "Total Emails Sent": "Total des e-mails envoyés",
        "Emails Successfully Sent": "E-mails envoyés avec succès",
        "Emails Failed to Send": "E-mails non envoyés",
        "A detailed log has been recorded below.": "Un journal détaillé a été enregistré ci-dessous.",
        "Generation Log": "Journal de génération",
        # New strings for the results page
        "Sending complete": "Envoi terminé",
        "All emails have been sent or an attempt has been made for each contact.": "Tous les e-mails ont été envoyés ou une tentative a été faite pour chaque contact.",
        "Sending Log": "Journal d'envoi",
        "Total Contacts": "Total des contacts",
        "This app has encountered an error.": "Cette application a rencontré une erreur.",
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
    Translates a given key into the selected language.
    Handles placeholders for dynamic text.
    """
    lang_code = _selected_lang
    if lang_code not in TRANSLATIONS:
        lang_code = DEFAULT_LANG
    
    translation_text = TRANSLATIONS[lang_code].get(key, key)
    
    # Use f-string-like formatting for placeholders
    if kwargs:
        try:
            return translation_text.format(**kwargs)
        except (KeyError, IndexError):
            # Fallback to returning the raw string with kwargs for debugging
            return f"{translation_text} {kwargs}"
    
    return translation_text