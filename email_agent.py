# email_agent.py

import openai
import json
import re # Added for regex
import os
from config import OPENAI_API_KEY # Import the API key from the config file

class SmartEmailAgent:
    """
    A unified AI agent for generating email content using OpenAI's models.
    It can generate both personalized emails for a specific contact and
    general templates based on a user's prompt.
    """
    def __init__(self, openai_api_key=OPENAI_API_KEY, model="gpt-4o"):
        if not openai_api_key:
            raise ValueError("OpenAI API Key is required for SmartEmailAgent.")
        
        self.openai_api_key = openai_api_key
        self.model = model

    def generate_email(self, prompt, contact_info=None, user_email_context="", output_language="en"):
        """
        Generates an email subject and body using OpenAI's GPT model.
        Can generate a personalized email or a general template.

        Args:
            prompt (str): The user's request for the email content.
            contact_info (dict, optional): The dictionary with recipient's info
                (e.g., {'name': 'John Doe', 'email': 'john@example.com'}).
                If None, a general template is generated.
            user_email_context (str): Additional context or style preferences for the email.
            output_language (str): The desired language for the email output (e.g., "en", "fr").

        Returns:
            dict: A dictionary containing 'subject' and 'body' of the generated email.
                  If a template is generated, 'name' will be a placeholder like '{{Name}}'.
        """
        # Adjust the system message based on personalization
        if contact_info and 'name' in contact_info:
            personalize = True
            name_placeholder = contact_info['name']
            
            system_message = f"""
            You are an expert email marketing assistant. Your task is to craft a professional, personalized email for a single recipient based on a user's request.
            The user will provide a prompt and a dictionary of recipient information.
            You MUST use the recipient's information to personalize the email.
            Your output MUST be a JSON object with two keys: "subject" and "body".
            The output language must be in {output_language}.
            The JSON object MUST be the only content in your response.
            """

            user_message_parts = [
                f"User request: {prompt}",
                f"Recipient's information: {json.dumps(contact_info, indent=2)}",
                f"Output language: {output_language}"
            ]
            if user_email_context:
                user_message_parts.append(f"Additional context/style preferences: {user_email_context}")
            
            user_message = "\n".join(user_message_parts)
            
        else:
            personalize = False
            name_placeholder = "{{Name}}"
            
            system_message = f"""
            You are an expert email marketing assistant. Your task is to craft a professional email template based on a user's request.
            You MUST use placeholders for any personal information, such as '{{Name}}' for the recipient's name.
            Your output MUST be a JSON object with two keys: "subject" and "body".
            The output language must be in {output_language}.
            The JSON object MUST be the only content in your response.
            """

            user_message_parts = [
                f"Generate an email template based on the following request: {prompt}",
                f"Use '{{Name}}' as a placeholder for the recipient's name in the greeting.",
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
            
            # Use the parsed content with a fallback
            subject = parsed_content.get("subject", "No Subject Generated")
            body = parsed_content.get("body", "No Body Generated")
            
            # For templated emails, ensure the placeholder is used
            if not personalize:
                body = body.replace(name_placeholder, "{{Name}}")
            
            return {
                "subject": subject,
                "body": body,
                "raw_llm_output": email_content
            }
        except openai.APIError as e:
            print(f"OpenAI API Error: {e}")
            return {"subject": "Error", "body": f"OpenAI API Error: {e}", "raw_llm_output": str(e)}
        except json.JSONDecodeError as jde:
            print(f"JSON Decode Error: {jde}")
            return {"subject": "Error", "body": f"Error parsing AI response: {jde}", "raw_llm_output": "AI response was not valid JSON."}
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return {"subject": "Error", "body": f"An unexpected error occurred: {e}", "raw_llm_output": str(e)}


if __name__ == '__main__':
    # --- For Testing: Test the AI agent's email generation ---
    # This requires a valid OPENAI_API_KEY environment variable.
    # To run this file directly, set OPENAI_API_KEY in your environment.
    # e.g., export OPENAI_API_KEY="sk-..."
    agent = SmartEmailAgent(openai_api_key=os.getenv("OPENAI_API_KEY"))
    
    sample_contact = {
        'name': 'John Doe',
        'email': 'john.doe@example.com',
        'company': 'Acme Corp',
        'product': 'Ultimate Widget',
        'last_interaction': '2025-06-01'
    }
    user_instruction = "Craft a follow-up email after their purchase of the {{product}}. Thank them, offer support, and subtly suggest an upgrade."

    print("--- Testing Personalized Agent ---")
    preview = agent.generate_email(user_instruction, sample_contact, output_language="en")
    print("Email Subject Preview:", preview.get("subject"))
    print("Email Body Preview:\n", preview.get("body"))
    print("-" * 20)
    
    print("--- Testing Template Agent ---")
    template = agent.generate_email(user_instruction, personalize=False, output_language="en")
    print("Template Subject Preview:", template.get("subject"))
    print("Template Body Preview:\n", template.get("body"))