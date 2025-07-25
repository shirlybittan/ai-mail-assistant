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
        # Initialize the OpenAI client directly with the API key
        self.client = openai.OpenAI(api_key=self.openai_api_key)
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
        The output should be a JSON object with two keys: "subject" and "body".
        The 'body' MUST be in HTML format to preserve formatting, including paragraphs and line breaks. Use <p> tags for paragraphs and <br> for line breaks. Do not include <html>, <head>, or <body> tags, only the content for the body.
        The email content should be engaging and clear.
        Use placeholders like {{Name}}, {{Email}}, {{Company}}, {{Position}}, {{Custom_Field}} where dynamic data is expected. Ensure these placeholders are enclosed in double curly braces `{{ }}`.
        Ensure the language of the output matches the requested output_language: {output_language}.

        Example JSON Output:
        {{
            "subject": "Welcome, {{Name}}! Your Account is Ready",
            "body": "<p>Hello {{Name}},</p><p>Welcome to our service! We're excited to have you on board.</p><p>To get started, please visit our tutorial at <a href='https://example.com/tutorial'>https://example.com/tutorial</a>.</p><p>Best regards,<br>The Team</p>"
        }}
        """

        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": prompt}
        ]
        if user_email_context:
            messages.append({"role": "user", "content": f"Additional context: {user_email_context}"})

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                response_format={"type": "json_object"},
                temperature=0.7,
                max_tokens=1000
            )

            email_content = response.choices[0].message.content
            parsed_content = json.loads(email_content)
            
            # Sanitize the output to ensure placeholders are correct and valid
            sanitized_subject = re.sub(r'\{([A-Za-z_]+)\}', r'{{\1}}', parsed_content.get("subject", "No Subject Generated"))
            sanitized_body = re.sub(r'\{([A-Za-z_]+)\}', r'{{\1}}', parsed_content.get("body", "No Body Generated"))
            
            return {
                "subject": sanitized_subject,
                "body": sanitized_body
            }
        except openai.APIError as e:
            print(f"OpenAI API Error: {e}")
            return {"subject": "Error", "body": f"Error generating email: {e}"}
        except json.JSONDecodeError as e:
            print(f"JSON Decode Error: {e}. Raw response: {email_content}")
            return {"subject": "Error", "body": f"Error parsing AI response: {e}. Raw: {email_content}"}
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return {"subject": "Error", "body": f"An unexpected error occurred: {e}"}


if __name__ == '__main__':
    # --- For Testing: Test the AI agent's email generation ---
    # This block is for local testing and assumes OPENAI_API_KEY is in your environment variables or .env
    # For Streamlit Cloud, the key is accessed via st.secrets, not os.getenv() in config.py's APP_CREDENTIALS
    
    # Temporarily set a dummy key for local testing if not already set,
    # as config.py might not have loaded it yet for standalone runs.
    if "OPENAI_API_KEY" not in os.environ:
        print("OPENAI_API_KEY not found in environment. Please set it for local testing.")
        # os.environ["OPENAI_API_KEY"] = "sk-your-test-key-here" # Uncomment and replace for local testing
        # Or ensure you run this with `python -m dotenv run your_script.py` if using a .env file locally

    try:
        agent = SmartEmailAgent(openai_api_key=os.getenv("OPENAI_API_KEY"))
        
        user_instruction = "Craft a follow-up email to new users. Thank them for signing up and offer a link to the tutorial. Make it warm and friendly."

        print("\n--- Testing Template Agent (English) ---")
        template_en = agent.generate_email_template(user_instruction, output_language="en")
        print("Subject (EN):", template_en["subject"])
        print("Body (EN):", template_en["body"])
        print("\n" + "="*50 + "\n")

        print("--- Testing Template Agent (French) ---")
        template_fr = agent.generate_email_template(user_instruction, output_language="fr")
        print("Subject (FR):", template_fr["subject"])
        print("Body (FR):", template_fr["body"])

    except ValueError as e:
        print(f"Initialization Error: {e}")
    except Exception as e:
        print(f"An error occurred during testing: {e}")