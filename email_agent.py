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
        self.model = model

    def generate_email_template(self, prompt, user_email_context="", output_language="en"):
        """
        Generates an email subject and body template using OpenAI's GPT model.
        The template will contain placeholders like {{Name}} and {{Email}}.
        
        Args:
            prompt (str): The user's request for the email content.
            user_email_context (str): Additional context or style preferences for the email.
            output_language (str): The desired language for the email output (e.g., "en", "fr").

        Returns:
            dict: A dictionary containing 'subject' and 'body' of the generated email template.
        """

        system_message = f"""
        You are an expert email marketing assistant. Your task is to craft a professional email template based on the user's instructions.
        The response must be in JSON format with keys 'subject' and 'body'.
        
        CRUCIAL INSTRUCTION: You MUST use placeholders for dynamic content.
        - Use '{{Name}}' for the recipient's name.
        - Use '{{Email}}' for the recipient's email address.
        - Do NOT invent other placeholders.
        
        Example of a perfect response format:
        {{
            "subject": "Follow-up regarding your recent purchase, {{Name}}!",
            "body": "Dear {{Name}},\n\nThank you for your recent purchase. We hope you are enjoying our products.\n\nBest regards,\nThe Team"
        }}
        
        The generated email must be in the language: {output_language}.
        """

        user_message_parts = [
            f"Generate an email template based on the following request: {prompt}",
            f"Output language: {output_language}"
        ]

        if user_email_context:
            user_message_parts.append(f"Additional context/style preferences: {user_email_context}")

        user_message = "\n".join(user_message_parts)

        try:
            client = openai.OpenAI(api_key=self.openai_api_key)
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": user_message}
                ],
                response_format={"type": "json_object"}
            )

            email_content = response.choices[0].message.content
            parsed_content = json.loads(email_content)
            
            # Sanitize the output to ensure placeholders are correct and valid
            sanitized_subject = re.sub(r'\{([A-Za-z]+)\}', r'{{\1}}', parsed_content.get("subject", "No Subject Generated"))
            sanitized_body = re.sub(r'\{([A-Za-z]+)\}', r'{{\1}}', parsed_content.get("body", "No Body Generated"))
            
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
    agent = SmartEmailAgent(openai_api_key=os.getenv("OPENAI_API_KEY"))
    
    user_instruction = "Craft a follow-up email to new users. Thank them for signing up and offer a link to the tutorial."

    print("--- Testing Template Agent ---")
    template = agent.generate_email_template(user_instruction, output_language="en")
    print("Template Subject Preview:", template.get("subject"))
    print("Template Body Preview:\n", template.get("body"))