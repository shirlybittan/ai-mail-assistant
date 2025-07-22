# translations.py

import streamlit as st

LANGUAGES = {
    "en": "English",
    "fr": "Français"
}

TRANSLATIONS = {
    # UI elements
    "AI Email Assistant": {"en": "AI Email Assistant", "fr": "Assistant E-mail IA"},
    "Configuration": {"en": "Configuration", "fr": "Configuration"},
    "Upload your contacts Excel file": {"en": "Upload your contacts Excel file", "fr": "Téléchargez votre fichier Excel de contacts"},
    "Add Attachments (Optional)": {"en": "Add Attachments (Optional)", "fr": "Ajouter des Pièces Jointes (Optionnel)"},
    "Email Content Request": {"en": "Email Content Request", "fr": "Demande de Contenu d'E-mail"},
    "Describe the email you want to send:": {"en": "Describe the email you want to send:", "fr": "Décrivez l'e-mail que vous souhaitez envoyer :"},
    "Optional: Provide context about your email style or content preferences...": {"en": "Optional: Provide context about your email style or content preferences (e.g., 'I prefer concise, direct language and a friendly tone.')", "fr": "Optionnel : Fournissez un contexte sur votre style d'e-mail ou vos préférences de contenu (ex: 'Je préfère un langage concis et direct et un ton amical.')"},
    "Personalize each email (uses contact name and makes it unique)": {"en": "Personalize each email (uses contact name and makes it unique)", "fr": "Personnaliser chaque e-mail (utilise le nom du contact et le rend unique)"},
    "Generate Emails": {"en": "Generate Emails", "fr": "Générer les E-mails"},
    "Generate Emails for Contacts": {"en": "Générer les E-mails pour les Contacts", "fr": "Générer les E-mails pour les Contacts"},
    "Please upload an Excel file with contacts first.": {"en": "Please upload an Excel file with contacts first.", "fr": "Veuillez d'abord télécharger un fichier Excel de contacts."},
    "Please provide a description for the email.": {"en": "Please provide a description for the email.", "fr": "Veuillez fournir une description pour l'e-mail."},
    "OpenAI API Key not found. Cannot generate emails.": {"en": "OpenAI API Key not found. Cannot generate emails.", "fr": "Clé API OpenAI introuvable. Impossible de générer des e-mails."},
    "Error initializing AI agent: ": {"en": "Error initializing AI agent: ", "fr": "Erreur lors de l'initialisation de l'agent IA : "},
    "Please check your OpenAI API Key.": {"en": "Please check your OpenAI API Key.", "fr": "Veuillez vérifier votre clé API OpenAI."},
    "Generating emails...": {"en": "Generating emails...", "fr": "Génération des e-mails..."},
    "Generating email for ": {"en": "Generating email for ", "fr": "Génération de l'e-mail pour "},
    " emails!": {"en": " emails!", "fr": " e-mails !"}, # For "Generated X emails!"
    "Send Emails": {"en": "Send Emails", "fr": "Envoyer les E-mails"},
    "You are about to send emails to": {"en": "You are about to send emails to", "fr": "Vous êtes sur le point d'envoyer des e-mails à"},
    " contacts.": {"en": " contacts.", "fr": " contacts."}, # For "X contacts."
    "Sending Mode:": {"en": "Sending Mode:", "fr": "Mode d'envoi :"},
    "FULLY PERSONALIZED": {"en": "FULLY PERSONALIZED", "fr": "ENTIÈREMENT PERSONNALISÉ"},
    "TEMPLATE-BASED": {"en": "TEMPLATE-BASED", "fr": "BASÉ SUR UN MODÈLE"},
    "Confirm Send All Emails": {"en": "Confirm Send All Emails", "fr": "Confirmer l'envoi de tous les e-mails"},
    "--- Sending Emails ---": {"en": "--- Sending Emails ---", "fr": "--- Envoi des E-mails ---"},
    "Preparing ": {"en": "Preparing ", "fr": "Préparation de "},
    " attachment(s)...": {"en": " attachment(s)...", "fr": " pièce(s) jointe(s)..."},
    "Attachments prepared.": {"en": "Attachments prepared.", "fr": "Pièces jointes préparées."},
    "ERROR: Could not prepare attachments: ": {"en": "ERROR: Could not prepare attachments: ", "fr": "ERREUR : Impossible de préparer les pièces jointes : "},
    "Email sending aborted.": {"en": "Email sending aborted.", "fr": "Envoi d'e-mails annulé."},
    "Attempting to send email to ": {"en": "Attempting to send email to ", "fr": "Tentative d'envoi d'e-mail à "},
    "Email sent successfully to ": {"en": "Email sent successfully to ", "fr": "E-mail envoyé avec succès à "},
    "Failed to send email to ": {"en": "Failed to send email to ", "fr": "Échec de l'envoi de l'e-mail à "},
    "--- Sending Complete ---": {"en": "--- Sending Complete ---", "fr": "--- Envoi Terminé ---"},
    "All emails processed!": {"en": "All emails processed!", "fr": "Tous les e-mails traités !"},
    "Total contacts processed:": {"en": "Total contacts processed:", "fr": "Total des contacts traités :"},
    "Successful emails sent:": {"en": "E-mails envoyés avec succès :", "fr": "E-mails envoyés avec succès :"},
    "Failed or Skipped emails:": {"en": "Failed or Skipped emails:", "fr": "E-mails échoués ou ignorés :"},
    "Temporary attachments cleaned up.": {"en": "Temporary attachments cleaned up.", "fr": "Pièces jointes temporaires nettoyées."},
    "ERROR: Could not clean up temporary attachments: ": {"en": "ERROR: Could not clean up temporary attachments: ", "fr": "ERREUR : Impossible de nettoyer les pièces jointes temporaires : "},
    "Activity Log": {"en": "Activity Log", "fr": "Journal d'Activité"},
    "Start New Email Session": {"en": "Start New Email Session", "fr": "Commencer une Nouvelle Session E-mail"},
    "Preview Email Content": {"en": "Preview Email Content", "fr": "Aperçu du Contenu de l'E-mail"},
    "This is a preview of the FIRST email generated. The content will vary if 'Personalize Emails' is checked.": {"en": "This is a preview of the FIRST email generated. The content will vary if 'Personalize Emails' is checked.", "fr": "Ceci est un aperçu du PREMIER e-mail généré. Le contenu variera si 'Personnaliser les e-mails' est coché."},
    "From:": {"en": "From:", "fr": "De :"},
    "To:": {"en": "To:", "fr": "À :"},
    "Subject:": {"en": "Objet :", "fr": "Objet :"},
    "Upload photos, videos, or documents (recommended total size < 25MB per mail)": {"en": "Upload photos, videos, or documents (recommended total size < 25 Mo per e-mail)", "fr": "Téléchargez des photos, vidéos ou documents (taille totale recommandée < 25 Mo par e-mail)"},
    " file(s) selected for attachment.": {"en": " file(s) selected for attachment.", "fr": " fichier(s) sélectionné(s) pour la pièce jointe."},
    "Loaded ": {"en": "Loaded ", "fr": "Chargé "},
    " contacts.": {"en": " contacts.", "fr": " contacts."},
    "Some contacts had issues:": {"en": "Some contacts had issues:", "fr": "Certains contacts ont eu des problèmes :"},
    "Please upload an Excel file to proceed.": {"en": "Please upload an Excel file to proceed.", "fr": "Veuillez télécharger un fichier Excel pour continuer."},
    "Using sender email:": {"en": "Using sender email:", "fr": "Utilisation de l'e-mail d'expéditeur :"},
    "Sender email or password not found. Please configure them correctly in Streamlit Secrets under [app_credentials].": {"en": "Sender email or password not found. Please configure them correctly in Streamlit Secrets under [app_credentials].", "fr": "E-mail de l'expéditeur ou mot de passe introuvable. Veuillez les configurer correctement dans les Secrets Streamlit sous [app_credentials]."},
    "Error: Password not found for sender email:": {"en": "Error: Password not found for sender email:", "fr": "Erreur : Mot de passe introuvable pour l'e-mail de l'expéditeur :"},
    "Please check your Streamlit Secrets.": {"en": "Please check your Streamlit Secrets.", "fr": "Veuillez vérifier vos Secrets Streamlit."},
    "Upload an Excel file and generate emails to see the sending options.": {"en": "Upload an Excel file and generate emails to see the sending options.", "fr": "Téléchargez un fichier Excel et générez des e-mails pour voir les options d'envoi."},
    "Debugging Info (REMOVE AFTER TROUBLESHOOTING)": {"en": "Debugging Info (REMOVE AFTER TROUBLESHOOTING)", "fr": "Informations de débogage (À SUPPRIMER APRÈS LE DÉPANNAGE)"},
    "All secrets from st.secrets:": {"en": "All secrets from st.secrets:", "fr": "Tous les secrets de st.secrets :"},
    "Sender credentials (from config):": {"en": "Sender credentials (from config):", "fr": "Identifiants de l'expéditeur (depuis config) :"},
    "OpenAI key (from config):": {"en": "OpenAI key (from config):", "fr": "Clé OpenAI (depuis config) :"},
    "DEBUG: SENDER_EMAIL retrieved:": {"en": "DEBUG: SENDER_EMAIL retrieved:", "fr": "DÉBOGAGE : E-mail de l'expéditeur récupéré :"},
    "DEBUG: SENDER_PASSWORD present:": {"en": "DEBUG: SENDER_PASSWORD present:", "fr": "DÉBOGAGE : Mot de passe de l'expéditeur présent :"},
    "DEBUG: FAILED_EMAILS_LOG_PATH:": {"en": "DEBUG: FAILED_EMAILS_LOG_PATH:", "fr": "DÉBOGAGE : Chemin du log des e-mails échoués :"},
    "e.g., 'An invitation to our annual charity gala, highlighting guest speaker Jane Doe and live music.'": {
        "en": "e.g., 'An invitation to our annual charity gala, highlighting guest speaker Jane Doe and live music.'",
        "fr": "ex: 'Une invitation à notre gala de charité annuel, mettant en avant l'oratrice invitée Jane Doe et de la musique live.'"
    },
    "e.g., 'I prefer concise, direct language and a friendly tone.'": {
        "en": "e.g., 'I prefer concise, direct language and a friendly tone.'",
        "fr": "ex: 'Je préfère un langage concis et direct et un ton amical.'"
    },
}

# Helper function for translations
def _t(key):
    """Translates a given text key based on the current session language."""
    lang = st.session_state.get("language", "fr") # Default to French if not set
    # Fallback to English if current language translation is missing, then to key itself
    return TRANSLATIONS.get(key, {}).get(lang, TRANSLATIONS.get(key, {}).get("en", key))