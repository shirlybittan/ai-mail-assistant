# email_generator.py

import openai
import json # Ensure json is imported for parsing responses

class SmartEmailAgent:
    def __init__(self, openai_api_key):
        if not openai_api_key:
            raise ValueError("OpenAI API Key is required for SmartEmailAgent.")
        openai.api_key = openai_api_key

    def generate_email(self, prompt, contact_name=None, personalize=True, user_email_context="", output_language="en"):
        """
        Generates an email subject and body using OpenAI's GPT model.
        Can generate a personalized email or a general template.

        Args:
            prompt (str): The user's request for the email content.
            contact_name (str, optional): The name of the recipient for personalization. Required if personalize=True.
            personalize (bool): Whether to personalize the email. If False, a general template is generated.
            user_email_context (str): Additional context or style preferences for the email.
            output_language (str): The desired language for the email output (e.g., "en", "fr").

        Returns:
            dict: A dictionary containing 'subject' and 'body' of the generated email.
                  If personalize is False, 'contact_name' will be '{{Name}}' in the body for templating.
        """

        # Adjust the system message based on personalization
        if personalize:
            system_message = f"""
            You are an expert email marketing assistant. Your task is to craft professional,
            engaging, and effective email subjects and bodies.
            The emails should be personalized for the specific recipient.
            Always provide both a subject line and the email body.
            The output MUST be in the following JSON format:
            {{
                "subject": "Your Email Subject Here",
                "body": "Your Email Body Here"
            }}
            The email MUST be generated in {output_language} language.
            Ensure the tone and style are appropriate for marketing/outreach in that language.
            """
            user_message_parts = [
                f"Generate an email based on the following request: {prompt}",
                f"Target recipient name: {contact_name}",
                f"Output language: {output_language}"
            ]
        else:
            # For template generation, use a placeholder like {{Name}}
            system_message = f"""
            You are an expert email marketing assistant. Your task is to craft a professional,
            engaging, and effective email subject and body that can be used as a template.
            The email should be for marketing or outreach purposes.
            For the recipient's name, use the placeholder '{{Name}}' in the greeting (e.g., 'Dear {{Name}},').
            Always provide both a subject line and the email body.
            The output MUST be in the following JSON format:
            {{
                "subject": "Your Email Subject Here",
                "body": "Your Email Body Here"
            }}
            The email MUST be generated in {output_language} language.
            Ensure the tone and style are appropriate for marketing/outreach in that language.
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
            response = openai.chat.completions.create(
                model="gpt-4o", # Or "gpt-3.5-turbo" if you prefer
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": user_message}
                ],
                response_format={"type": "json_object"}
            )

            email_content = response.choices[0].message.content
            parsed_content = json.loads(email_content)
            return {
                "subject": parsed_content.get("subject", "No Subject Generated"),
                "body": parsed_content.get("body", "No Body Generated")
            }
        except openai.APIError as e:
            print(f"OpenAI API Error: {e}")
            return {"subject": "Error", "body": f"Error generating email: {e}"}
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return {"subject": "Error", "body": f"An unexpected error occurred: {e}"}