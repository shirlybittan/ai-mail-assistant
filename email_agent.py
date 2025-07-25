# email_agent.py

import openai
import json
import re
import os
from config import OPENAI_API_KEY

class SmartEmailAgent:
    """
    A unified AI agent for generating email content using OpenAI's models.
    It can generate a general email template with placeholders based on a user's prompt.
    """
    def __init__(self, openai_api_key=OPENAI_API_KEY, model="gpt-4o"):
        if not openai_api_key:
            raise ValueError("OpenAI API Key is required for SmartEmailAgent.")
            
        self.openai_api_key = openai_api_key
        # Initialize the OpenAI client here
        self.client = openai.OpenAI(api_key=self.openai_api_key)
        self.model = model

    def generate_email_template(self, prompt, user_email_context="", output_language="en", personalize_emails=False):
        """
        Generates an email subject and body template using OpenAI's GPT model.
        The template will contain placeholders like {{Name}} and {{Email}}.
        
        Args:
            prompt (str): The user's request for the email content.
            user_email_context (str): Additional context or style preferences for the email.
            output_language (str): The desired language for the email output (e.g., "en", "fr").
            personalize_emails (bool): If True, the agent should include personalization placeholders.

        Returns:
            dict: A dictionary containing 'subject' and 'body' of the generated email template.
        """

        personalization_hint = ""
        if personalize_emails:
            personalization_hint = "Include personalization placeholders like '{{Name}}' for the recipient's name and '{{Email}}' for their email address where appropriate."
        else:
            personalization_hint = "DO NOT include specific name or email placeholders like '{{Name}}' or '{{Email}}'. Use a generic greeting if necessary, but avoid explicit personalization markers."


        system_message = f"""
        You are an expert email marketing assistant. Your task is to craft a professional email template based on the user's instructions.
        The output must be a JSON object with two keys: "subject" and "body".
        Ensure the body uses standard newlines (\\n) for paragraphs and line breaks, not HTML tags like <p> or <br>.
        {personalization_hint}
        The email should be in {output_language}."""

        user_message_content = f"Instructions: {prompt}\n"
        if user_email_context:
            user_message_content += f"Additional context/style: {user_email_context}"

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": user_message_content}
                ]
            )

            email_content = response.choices[0].message.content
            parsed_content = json.loads(email_content)
            
            # Sanitize the output to ensure placeholders are correct and valid
            # Also, remove any residual HTML paragraph tags if the model occasionally generates them
            sanitized_subject = re.sub(r'\{([A-Za-z]+)\}', r'{{\1}}', parsed_content.get("subject", "No Subject Generated"))
            sanitized_body = re.sub(r'\{([A-Za-z]+)\}', r'{{\1}}', parsed_content.get("body", "No Body Generated"))
            
            # Remove <p> and </p> tags and replace with newlines for better plain text handling
            sanitized_body = sanitized_body.replace('<p>', '').replace('</p>', '\n\n').strip()
            # Replace <br> tags with newlines
            sanitized_body = sanitized_body.replace('<br>', '\n').strip()
            # Ensure proper line breaks are used, especially for lists or sequential paragraphs
            sanitized_body = re.sub(r'\n\s*\n', '\n\n', sanitized_body) # Collapse multiple newlines to just two

            return {
                "subject": sanitized_subject,
                "body": sanitized_body
            }
        except openai.APIError as e:
            print(f"OpenAI API Error: {e}")
            return {"subject": "Error", "body": f"Error generating email: {e}"}
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return {"subject": "Error", "body": f"An unexpected error occurred: {e}"}


if __name__ == '__main__':
    # --- For Testing: Test the AI agent's email generation ---
    # To run this test, ensure you have an OPENAI_API_KEY environment variable set
    # You can set it temporarily like: export OPENAI_API_KEY="your_key_here"
    # Or use a .env file with `python-dotenv` if you uncomment `load_dotenv()` below.
    # from dotenv import load_dotenv
    # load_dotenv() # Load environment variables from .env file

    agent = SmartEmailAgent(openai_api_key=os.getenv("OPENAI_API_KEY"))
    
    user_instruction = "Craft a follow-up email to new users. Thank them for signing up and offer a link to the tutorial."

    print("--- Testing Template Agent (Personalized) ---")
    template_personalized = agent.generate_email_template(
        user_instruction,
        user_email_context="Warm and friendly tone.",
        output_language="en",
        personalize_emails=True
    )
    print("Subject (Personalized):", template_personalized["subject"])
    print("Body (Personalized):\n", template_personalized["body"])

    print("\n--- Testing Template Agent (Generic) ---")
    template_generic = agent.generate_email_template(
        "Announce a new product feature. Keep it concise.",
        output_language="fr",
        personalize_emails=False
    )
    print("Subject (Generic - FR):", template_generic["subject"])
    print("Body (Generic - FR):\n", template_generic["body"])