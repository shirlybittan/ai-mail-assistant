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
        "Some contacts had issues and were skipped.": "Some contacts had issues and were skipped.",
        "Show skipped contacts": "Show skipped contacts",
        "Using previously loaded contacts: {count} valid contacts found.": "Using previously loaded contacts: {count} valid contacts found.",
        "Personalize emails for each contact?": "Personalize emails for each contact?",
        "Generic Greeting Placeholder (e.g., 'Dear Friends')": "Placeholder for {{Name}} (e.g., 'Friends', 'Valued Customers')",
        "Enter your instruction for the AI agent:": "Enter your instruction for the AI agent:",
        "AI Instruction": "AI Instruction",
        "e.g., 'Write a follow-up email to customers who purchased our new product. Thank them and offer a discount on their next purchase.'": "e.g., 'Write a follow-up email to customers who purchased our new product. Thank them and offer a discount on their next purchase.'",
        "Additional context for the email (optional):": "Additional context for the email (optional):",
        "Email Context": "Email Context",
        "e.g., 'Keep the tone professional but friendly.'": "e.g., 'Keep the tone professional but friendly.'",
        "Attachments (Optional)": "Attachments (Optional)",
        "Upload files to attach to all emails": "Upload files to attach to all emails",
        "You have uploaded {count} attachments.": "You have uploaded {count} attachments.",
        "No attachments uploaded.": "No attachments uploaded.",
        "Generated Email Template": "Generated Email Template",
        "Proceed to Preview": "Proceed to Preview",
        "Generating email template... This may take a moment.": "Generating email template... This may take a moment.",
        "Template email generated successfully!": "Template email generated successfully!",
        "ERROR: Failed to generate template email. Details: {details}": "ERROR: Failed to generate template email. Details: {details}",
        
        "2. Aperçu et envoi": "2. Preview and Send",
        "Review and edit the generated email template below. Click the preview button to see how it looks for the first contact.": "Review and edit the generated email template below. Click the preview button to see how it looks for the first contact.",
        "Email Preview": "Email Preview",
        "Live Preview (Example for First Contact)": "Live Preview (Example for First Contact)",
        "Edit Template": "Edit Template",
        "Show/Update Preview": "Show/Update Preview",
        "Preview Subject": "Preview Subject",
        "Preview Body": "Preview Body",
        "Confirm Send": "Confirm Send",
        "Preparing emails for sending...": "Preparing emails for sending...",
        "Email sending process initiated...": "Email sending process initiated...",
        "--- [{current}/{total}] Processing contact: {name} ({email}) ---": "--- [{current}/{total}] Processing contact: {name} ({email}) ---",
        "  Attempting Email for {name}...": "  Attempting Email for {name}...",
        "    - Email: success - Email sent to {email} successfully.": "    - Email: success - Email sent to {email} successfully.",
        "    - Email: error - Failed to send to {email}. Details: {details}": "    - Email: error - Failed to send to {email}. Details: {details}",
        "--- Email sending process complete ---": "--- Email sending process complete ---",
        "ERROR: Could not clean up temporary attachments: ": "ERROR: Could not clean up temporary attachments: ",

        "3. Résultats d'envoi": "3. Sending Results",
        "Start New Email Session": "Start New Email Session",
        "All emails sent successfully!": "All emails sent successfully!",
        "All {count} emails were sent without any issues.": "All {count} emails were sent without any issues.",
        "Sending complete with errors.": "Sending complete with errors.",
        "Some emails failed to send. Please check the log below for details.": "Some emails failed to send. Please check the log below for details.",
        "Summary": "Summary",
        "Total Contacts": "Total Contacts",
        "Emails Successfully Sent": "Emails Successfully Sent",
        "Emails Failed to Send": "Emails Failed to Send",
        "Show Activity Log and Errors": "Show Activity Log and Errors"
    },
    "fr": {
        "AI Email Assistant": "Assistant d'E-mail IA",
        "Welcome to the AI Email Assistant!": "Bienvenue dans l'Assistant d'E-mail IA !",
        "Select your language": "Sélectionnez votre langue",
        "Generate Email": "Générer l'e-mail",
        "Compose your email details below.": "Composez les détails de votre e-mail ci-dessous.",
        "Recipient": "Destinataire",
        "Subject": "Objet",
        "Body": "Corps",
        "Sender": "Expéditeur",
        "Clear Form": "Effacer le Formulaire",
        "Your email has been generated!": "Votre e-mail a été généré !",
        "Error generating email. Please try again.": "Erreur lors de la génération de l'e-mail. Veuillez réessayer.",
        "Recipient, Subject, and Body cannot be empty.": "Le destinataire, l'objet et le corps ne peuvent pas être vides.",
        "Enter a recipient": "Saisir un destinataire",
        "Enter a subject": "Saisir un objet",
        "Enter email body": "Saisir le corps de l'e-mail",
        "Enter sender name or email": "Saisir le nom ou l'e-mail de l'expéditeur",
        # New Translations
        "1. Email Generation": "1. Génération d'e-mails",
        "Upload an Excel file with contacts (.xlsx)": "Téléchargez un fichier Excel avec les contacts (.xlsx)",
        "Successfully loaded {count} valid contacts.": "Chargement réussi de {count} contacts valides.",
        "Some contacts had issues and were skipped.": "Certains contacts avaient des problèmes et ont été ignorés.",
        "Show skipped contacts": "Afficher les contacts ignorés",
        "Using previously loaded contacts: {count} valid contacts found.": "Utilisation des contacts précédemment chargés : {count} contacts valides trouvés.",
        "Personalize emails for each contact?": "Personnaliser les e-mails pour chaque contact ?",
        "Generic Greeting Placeholder (e.g., 'Dear Friends')": "Remplaçant pour {{Name}} (ex: 'Chers Amis', 'Clients')",
        "Enter your instruction for the AI agent:": "Saisissez votre instruction pour l'agent IA :",
        "AI Instruction": "Instruction pour l'IA",
        "e.g., 'Write a follow-up email to customers who purchased our new product. Thank them and offer a discount on their next purchase.'": "ex. : 'Rédigez un e-mail de suivi pour les clients qui ont acheté notre nouveau produit. Remerciez-les et offrez-leur une réduction sur leur prochain achat.'",
        "Additional context for the email (optional):": "Contexte supplémentaire pour l'e-mail (facultatif) :",
        "Email Context": "Contexte de l'e-mail",
        "e.g., 'Keep the tone professional but friendly.'": "ex. : 'Gardez un ton professionnel mais amical.'",
        "Attachments (Optional)": "Pièces jointes (facultatif)",
        "Upload files to attach to all emails": "Téléchargez des fichiers à joindre à tous les e-mails",
        "You have uploaded {count} attachments.": "Vous avez téléchargé {count} pièces jointes.",
        "No attachments uploaded.": "Aucune pièce jointe téléchargée.",
        "Generated Email Template": "Modèle d'e-mail généré",
        "Proceed to Preview": "Passer à l'aperçu",
        "Generating email template... This may take a moment.": "Génération du modèle d'e-mail... Cela peut prendre un moment.",
        "Template email generated successfully!": "Modèle d'e-mail généré avec succès !",
        "ERROR: Failed to generate template email. Details: {details}": "ERREUR : Échec de la génération du modèle d'e-mail. Détails : {details}",

        "2. Aperçu et envoi": "2. Aperçu et envoi",
        "Review and edit the generated email template below. Click the preview button to see how it looks for the first contact.": "Vérifiez et modifiez le modèle d'e-mail ci-dessous. Cliquez sur le bouton d'aperçu pour voir à quoi il ressemble pour le premier contact.",
        "Email Preview": "Aperçu de l'e-mail",
        "Live Preview (Example for First Contact)": "Aperçu en direct (Exemple pour le premier contact)",
        "Edit Template": "Modifier le modèle",
        "Show/Update Preview": "Voir l'aperçu / Mettre à jour",
        "Preview Subject": "Objet de l'aperçu",
        "Preview Body": "Corps de l'aperçu",
        "Confirm Send": "Confirmer l'envoi",
        "Preparing emails for sending...": "Préparation des e-mails pour l'envoi...",
        "Email sending process initiated...": "Processus d'envoi d'e-mails initié...",
        "--- [{current}/{total}] Processing contact: {name} ({email}) ---": "--- [{current}/{total}] Traitement du contact : {name} ({email}) ---",
        "  Attempting Email for {name}...": "  Tentative d'envoi de l'e-mail pour {name}...",
        "    - Email: success - Email sent to {email} successfully.": "    - E-mail : succès - E-mail envoyé avec succès à {email}.",
        "    - Email: error - Failed to send to {email}. Details: {details}": "    - E-mail : erreur - Échec de l'envoi à {email}. Détails : {details}",
        "--- Email sending process complete ---": "--- Processus d'envoi d'e-mails terminé ---",
        "ERROR: Could not clean up temporary attachments: ": "ERREUR : Impossible de nettoyer les pièces jointes temporaires : ",

        "3. Résultats d'envoi": "3. Résultats d'envoi",
        "Start New Email Session": "Commencer une nouvelle session",
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
    translation = TRANSLATIONS.get(_selected_lang, {}).get(key, key)
    return translation.format(**kwargs)