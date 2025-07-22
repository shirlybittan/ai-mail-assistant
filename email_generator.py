# email_generator.py

import openai

class SmartEmailAgent:
    def __init__(self, openai_api_key):
        if not openai_api_key:
            raise ValueError("OpenAI API Key is required for SmartEmailAgent.")
        openai.api_key = openai_api_key

    def generate_email(self, prompt, contact_name, personalize, user_email_context="", output_language="en"):
        """
        Generates an email subject and body using OpenAI's GPT model.

        Args:
            prompt (str): The user's request for the email content.
            contact_name (str): The name of the recipient for personalization.
            personalize (bool): Whether to personalize the email.
            user_email_context (str): Additional context or style preferences for the email.
            output_language (str): The desired language for the email output (e.g., "en", "fr").

        Returns:
            dict: A dictionary containing 'subject' and 'body' of the generated email.
        """

        system_message = f"""
        You are an expert email marketing assistant. Your task is to craft professional,
        engaging, and effective email subjects and bodies.
        The emails should be for marketing or outreach purposes.
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
            f"Should be personalized for {contact_name}: {personalize}",
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
            # Assuming the model reliably returns JSON, parse it
            import json
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