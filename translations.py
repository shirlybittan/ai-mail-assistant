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
        # Add more English translations here
    },
    "fr": {
        "AI Email Assistant": "Assistant d'E-mail IA",
        "Welcome to the AI Email Assistant!": "Bienvenue dans l'Assistant d'E-mail IA !",
        "Select your language": "Sélectionnez votre langue",
        "Generate Email": "Générer l'E-mail",
        "Compose your email details below.": "Rédigez les détails de votre e-mail ci-dessous.",
        "Recipient": "Destinataire",
        "Subject": "Objet",
        "Body": "Corps du Message",
        "Sender": "Expéditeur",
        "Clear Form": "Effacer le Formulaire",
        "Your email has been generated!": "Votre e-mail a été généré !",
        "Error generating email. Please try again.": "Erreur lors de la génération de l'e-mail. Veuillez réessayer.",
        "Recipient, Subject, and Body cannot be empty.": "Le destinataire, l'objet et le corps ne peuvent pas être vides.",
        "Enter a recipient": "Saisir un destinataire",
        "Enter a subject": "Saisir un objet",
        "Enter email body": "Saisir le corps de l'e-mail",
        "Enter sender name or email": "Saisir le nom ou l'e-mail de l'expéditeur",
        # Add more French translations here
    }
}

# Default language if no session state is set
DEFAULT_LANG = "fr"

# Global variable to store the selected language
_selected_lang = DEFAULT_LANG

def set_language(lang_code):
    """Sets the global language for translations."""
    global _selected_lang
    if lang_code in LANGUAGES:
        _selected_lang = lang_code
    else:
        _selected_lang = DEFAULT_LANG # Fallback to default if invalid code

def _t(key, lang_code=None):
    """
    Translates a given key into the selected language.
    If lang_code is provided, it overrides the global selected language for this call.
    """
    current_lang = lang_code if lang_code in LANGUAGES else _selected_lang
    return TRANSLATIONS.get(current_lang, {}).get(key, key) # Fallback to key itself if not found