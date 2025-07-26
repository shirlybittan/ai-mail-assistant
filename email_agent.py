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
            dict: A dictionary containing 'subject' and 'body' of the generated email.
                  Returns {"subject": "Error", "body": "..."} on failure.
        """
        system_message = f"""You are an AI assistant specialized in crafting professional and engaging email templates.
Your task is to generate an email subject and body based on the user's prompt and additional context.
The output MUST be in a JSON format with two keys: "subject" and "body".

Example JSON output:
```json
{{
  "subject": "Your Subject Here",
  "body": "Your email body here. Use {{Name}} for recipient's name and {{Email}} for recipient's email if personalized greetings are allowed."
}}