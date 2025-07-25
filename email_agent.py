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

    def generate_email_template(self, prompt, user_email_context="", output_language="en", personalize_emails=True):
        """
        Generates an email subject and body template using OpenAI's GPT model.
        The template will contain placeholders like {{Name}} and {{Email}} if personalization is enabled.
        
        Args:
            prompt (str): The user's request for the email content.
            user_email_context (str): Additional context or style preferences for the email.
            output_language (str): The desired language for the email output (e.g., "en", "fr").
            personalize_emails (bool): Flag indicating if personalization placeholders should be used.

        Returns:
            dict: A dictionary containing 'subject' and 'body' of the generated email template.
        """

        system_message = f"""
        You are an expert email marketing assistant. Your task is to craft a professional email template based on the user's instructions.
        The template must be a valid JSON object with two keys: "subject" and "body".
        Ensure the output is ONLY the JSON object, with no additional text or formatting outside of it.
        The email body should be clear, concise, and use appropriate line breaks and paragraph spacing.

        If personalization is enabled (user desires it, 'personalize_emails' is true), use placeholders like {{Name}} for the recipient's name and {{Email}} for their email address where appropriate.
        If personalization is NOT enabled (user does not desire it, 'personalize_emails' is false), craft a general template and avoid using specific name/email placeholders. Instead, use a generic greeting like "Hello" or "Dear Customer/Recipient".

        Example for personalized template:
        {{
            "subject": "Hello {{Name}}! Here's an Update for You",
            "body": "Hi {{Name}},\n\nWe hope this email finds you well. Your email is {{Email}}.\n\nHere's some news..."
        }}

        Example for non-personalized/generic template:
        {{
            "subject": "Important Update for Our Valued Customers",
            "body": "Dear Valued Customer,\n\nWe are pleased to announce some exciting news. Please read on for more details.\n\nBest regards,"
        }}

        Ensure the subject is engaging and the body is well-structured with appropriate line breaks (use \\n for newlines).
        """

        user_message_content = f"User's instruction: {prompt}\n"
        if user_email_context:
            user_message_content += f"Additional context/style: {user_email_context}\n"
        
        if personalize_emails:
            user_message_content += "Please create a template that uses personalization placeholders like {{Name}} and {{Email}} where appropriate in the subject and body."
        else:
            user_message_content += "Please create a general template. Do NOT use personalization placeholders like {{Name}} or {{Email}}. Use a generic greeting (e.g., 'Dear Customer', 'Hello there') in the template."
            
        user_message_content += f"The output language for the subject and body should be in {output_language}."

        try:
            response = openai.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": user_message_content}
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
        except json.JSONDecodeError as e:
            print(f"JSON Decode Error: {e}. Raw response: {email_content}")
            return {"subject": "Error", "body": f"Could not parse AI response (JSON Error): {e}. Response was: {email_content[:200]}..."}
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return {"subject": "Error", "body": f"An unexpected error occurred: {e}"}


if __name__ == '__main__':
    # --- For Testing: Test the AI agent's email generation ---
    # Ensure OPENAI_API_KEY is set in your environment variables for testing
    # export OPENAI_API_KEY="your_key_here"
    agent = SmartEmailAgent(openai_api_key=os.getenv("OPENAI_API_KEY"))
    
    # Test personalized email
    user_instruction_personalized = "Craft a welcome email for new users, inviting them to explore our features."
    print("--- Testing Personalized Template Agent ---")
    template_personalized = agent.generate_email_template(
        prompt=user_instruction_personalized,
        output_language="en",
        personalize_emails=True
    )
    print("Personalized Template:")
    print(f"Subject: {template_personalized['subject']}")
    print(f"Body: {template_personalized['body']}\n")

    # Test generic email
    user_instruction_generic = "Send out a general announcement about upcoming maintenance."
    print("--- Testing Generic Template Agent ---")
    template_generic = agent.generate_email_template(
        prompt=user_instruction_generic,
        output_language="en",
        personalize_emails=False
    )
    print("Generic Template:")
    print(f"Subject: {template_generic['subject']}")
    print(f"Body: {template_generic['body']}\n")