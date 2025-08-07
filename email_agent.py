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
                  Returns error message if generation fails.
        """

        personalization_hint = ""
        if personalize_emails:
            # If personalization is ON, instruct AI to use placeholders.
            personalization_hint = "INCLUDE specific name and email placeholders where appropriate (e.g., 'Dear {{Name}}', 'contact us at {{Email}}')."
        else:
            # If personalization is OFF, instruct AI NOT to use placeholders and NOT to include a greeting.
            # The application will prepend a generic greeting later.
            personalization_hint = "DO NOT include any name or email placeholders (like '{{Name}}' or '{{Email}}'). DO NOT include any salutation (e.g., 'Dear', 'Hello', 'Bonjour', 'Salut'). Start directly with the main body of the email content. The application will add a generic greeting or salutation if necessary."

        system_message = (
            "You are an AI assistant specialized in drafting professional and effective email templates. "
            "Your task is to generate an email subject and body based on the user's instructions. "
            "The output MUST be a JSON object with two keys: 'subject' and 'body'. "
            f"The email should be in {output_language} language.\n\n"
            "Here are the rules for generating the email:\n"
            f"- {personalization_hint}\n"
            "- Ensure the email content is relevant to the prompt and context.\n"
            "- The 'body' should be a single string, including paragraph breaks (use '\\n\\n' for new paragraphs).\n"
            "- Avoid conversational filler like 'Here is the email:' or 'Subject: ... Body: ...'."
        )

        user_message_content = f"User's request: {prompt}"
        if user_email_context:
            user_message_content += f"\nAdditional context/style: {user_email_context}"

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": user_message_content}
                ],
                response_format={"type": "json_object"}
            )

            # Extract content and parse JSON
            response_content = response.choices[0].message.content
            email_template = json.loads(response_content)

            # Basic validation
            if "subject" not in email_template or "body" not in email_template:
                raise ValueError("AI response missing 'subject' or 'body' key.")

            # Clean up body to remove potential leading/trailing whitespace or accidental AI salutations
            email_template['body'] = email_template['body'].strip()
            # Further refinement: Remove common salutations if they accidentally slipped through
            # This is a fallback in case the AI ignores the system prompt.
            common_salutations_regex = r"^(Dear|Hello|Hi|Bonjour|Salut|Chers?|Cher|Chère)\s+[^,\n]*[,!.]?\s*\n\n*"
            email_template['body'] = re.sub(common_salutations_regex, "", email_template['body'], flags=re.IGNORECASE | re.MULTILINE)
            email_template['body'] = email_template['body'].strip()


            return email_template

        except json.JSONDecodeError as e:
            return {"subject": "Error", "body": f"Failed to parse AI response (JSON error): {e}. Raw: {response_content}"}
        except ValueError as e:
            return {"subject": "Error", "body": f"AI response validation error: {e}. Raw: {response_content}"}
        except openai.APIError as e:
            return {"subject": "Error", "body": f"OpenAI API Error: {e}"}
        except Exception as e:
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
    print("Subject (Generic):", template_generic["subject"])
    print("Body (Generic):\n", template_generic["body"])

    print("\n--- Testing Template Agent (Generic with existing Salutation in prompt - should be removed by AI) ---")
    template_generic_with_salutation_prompt = agent.generate_email_template(
        "Write an email about a new discount. Start with 'Hello Team,'.",
        output_language="en",
        personalize_emails=False
    )
    print("Subject (Generic, prompt with Salutation):", template_generic_with_salutation_prompt["subject"])
    print("Body (Generic, prompt with Salutation):\n", template_generic_with_salutation_prompt["body"])