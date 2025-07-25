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
        self.client = openai.OpenAI(api_key=self.openai_api_key)


    def generate_email_template(self, prompt, user_email_context="", output_language="en", allow_personalized_salutation_override=True):
        """
        Generates an email subject and body template using OpenAI's GPT model.
        The template will contain placeholders like {{Name}} and {{Email}}.

        Args:
            prompt (str): The user's request for the email content.
            user_email_context (str): Additional context or style preferences for the email.
            output_language (str): The desired language for the email output (e.g., "en", "fr").
            allow_personalized_salutation_override (bool): If True, explicitly tells the AI to use
                                                           a personalized salutation like 'Dear {{Name}}'.

        Returns:
            dict: A dictionary containing 'subject' and 'body' of the generated email template.
        """

        personalization_guidance = ""
        if allow_personalized_salutation_override:
            personalization_guidance = (
                "For the salutation, use 'Dear {{Name}}' (or its equivalent in the output language) "
                "to allow for personalization. Avoid generic salutations like 'Dear Customer' "
                "if a personalized one is possible."
            )

        system_message = f"""
        You are an expert email marketing assistant. Your task is to craft a professional email template based on the user's instructions.
        The output must be a JSON object with two keys: "subject" and "body".
        The email body should be in markdown format.
        You must use placeholders for dynamic content. The available placeholders are:
        - {{Name}}: for the recipient's name (e.g., John Doe, Alice Smith)
        - {{Email}}: for the recipient's email address

        {personalization_guidation}

        Ensure the subject line is concise and engaging.
        The email body should be well-structured with clear paragraphs and a professional tone.
        The output language must be {output_language}.

        Example JSON output:
        ```json
        {{
            "subject": "Your Exclusive Offer, {{Name}}!",
            "body": "Hi {{Name}},\\n\\nWe hope this email finds you well. We have a special offer just for you!\\n\\nClick here to learn more: [Link](https://example.com)\\n\\nBest regards,\\nYour Team"
        }}
        ```
        """

        user_message_content = f"User instruction: {prompt}\n"
        if user_email_context:
            user_message_content += f"Additional context/style: {user_email_context}\n"

        try:
            response = self.client.chat.completions.create(
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
            # Converts {Placeholder} to {{Placeholder}}
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
            print(f"JSON Decode Error: Could not parse AI response. Error: {e}")
            print(f"AI response was: {email_content}")
            return {"subject": "Error", "body": f"Error parsing AI response: {e}. Raw response: {email_content}"}
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return {"subject": "Error", "body": f"An unexpected error occurred: {e}"}


if __name__ == '__main__':
    # --- For Testing: Test the AI agent's email generation ---
    # To run this test, ensure you have OPENAI_API_KEY set in your environment variables or config.py
    # Example: export OPENAI_API_KEY="your_api_key_here"
    agent = SmartEmailAgent(openai_api_key=os.getenv("OPENAI_API_KEY"))

    user_instruction = "Craft a follow-up email to new users. Thank them for signing up and offer a link to the tutorial."

    print("--- Testing Template Agent ---")
    template = agent.generate_email_template(
        prompt=user_instruction,
        user_email_context="Keep it friendly and concise.",
        output_language="en",
        allow_personalized_salutation_override=True
    )
    print(f"Generated Subject: {template['subject']}")
    print(f"Generated Body:\n{template['body']}")

    print("\n--- Testing Template Agent (French, no personalization override) ---")
    template_fr = agent.generate_email_template(
        prompt="Rédigez un e-mail de remerciement pour les participants à un webinaire.",
        user_email_context="Ton professionnel, bref.",
        output_language="fr",
        allow_personalized_salutation_override=False # Should allow generic salutation
    )
    print(f"Generated Subject (FR): {template_fr['subject']}")
    print(f"Generated Body (FR):\n{template_fr['body']}")