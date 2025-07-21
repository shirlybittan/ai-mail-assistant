# email_generator.py
import openai
import os
import json
import re # Used for robust parsing if JSON decoding fails

class SmartEmailAgent:
    def __init__(self, openai_api_key: str):
        """
        Initializes the SmartEmailAgent with the OpenAI API key.
        """
        if not openai_api_key:
            raise ValueError("OpenAI API key is required for SmartEmailAgent.")
        self.client = openai.OpenAI(api_key=openai_api_key)

    def generate_email(self, prompt: str, contact_name: str, personalize: bool, user_email_context: str) -> dict:
        """
        Generates a personalized or template-based email subject and body using OpenAI's API.

        Args:
            prompt (str): The user's main prompt for the email content.
            contact_name (str): The name of the contact (for personalization).
            personalize (bool): True if the email should be highly personalized, False for a general template.
            user_email_context (str): Additional context about the user's email style/content.

        Returns:
            dict: A dictionary with 'subject' and 'body' keys.
        """
        if not prompt:
            return {"subject": "No Subject", "body": "No email body generated due to empty prompt."}

        # Base instructions for the AI to ensure JSON output
        instructions = (
            "You are an AI assistant specialized in generating professional and engaging emails. "
            "Your task is to create an email subject and body based on the user's prompt. "
            "Always respond in JSON format with two keys: 'subject' and 'body'. "
            "Do NOT include any other text or formatting outside the JSON."
        )

        # Enhance instructions for personalization or template
        if personalize:
            personalization_instructions = (
                f"The email should be highly personalized for a contact named '{contact_name}'. "
                "Incorporate the contact's name naturally into the greeting and body. "
                "Ensure the tone is warm, relevant, and tailored to the individual. "
                "Avoid generic greetings like 'Dear [Name]' unless explicitly requested by the prompt. "
            )
        else:
            personalization_instructions = (
                "The email should be a general template, suitable for broad outreach. "
                "Do NOT include the contact's name directly in the email; use a general greeting. "
                "The tone should be professional and universally applicable. "
            )
        
        # Add user's email context if provided
        context_instruction = ""
        if user_email_context and user_email_context.strip():
            context_instruction = f"Consider the following context about my typical email style/content, but prioritize main instructions: '{user_email_context}'."

        # Combine all parts of the prompt
        full_prompt = (
            f"Generate an email based on the following instructions:\n"
            f"Main purpose: '{prompt}'.\n"
            f"{personalization_instructions}\n"
            f"{context_instruction}\n"
            "Ensure the final output is ONLY a JSON object with 'subject' and 'body' keys."
        )

        messages = [
            {"role": "system", "content": instructions},
            {"role": "user", "content": full_prompt}
        ]

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini", # Using gpt-4o-mini for good balance of cost and quality
                messages=messages,
                max_tokens=1000, # Max tokens for the AI's response
                temperature=0.7, # Adjust creativity (0.0-1.0)
                response_format={"type": "json_object"} # Explicitly ask for JSON output
            )

            raw_response_content = response.choices[0].message.content

            # Attempt to parse the JSON output from OpenAI
            try:
                email_data = json.loads(raw_response_content)
                subject = email_data.get("subject", "Generated Subject")
                body = email_data.get("body", "Generated email body.")
            except json.JSONDecodeError:
                # Fallback if OpenAI doesn't return perfect JSON
                print(f"WARNING: email_generator: Failed to decode JSON from OpenAI response. Attempting heuristic parse. Raw: {raw_response_content}")
                subject_match = re.search(r'"subject"\s*:\s*"(.*?)"', raw_response_content, re.DOTALL)
                body_match = re.search(r'"body"\s*:\s*"(.*?)"', raw_response_content, re.DOTALL)
                subject = subject_match.group(1) if subject_match else "Generated Subject (Parse Error)"
                body = body_match.group(1) if body_match else f"Generated email body (Parse Error). Please check raw response: {raw_response_content[:200]}..."

            return {"subject": subject, "body": body}

        except openai.APIError as e:
            # Handle specific OpenAI API errors (e.g., authentication, rate limits)
            print(f"OpenAI API Error: {e}")
            return {"subject": "Error", "body": f"Failed to generate email: OpenAI API Error - {e.status_code} {e.message}"}
        except openai.APITimeoutError as e:
            # Handle API timeouts
            print(f"OpenAI API Timeout: {e}")
            return {"subject": "Error", "body": f"Failed to generate email: OpenAI API Timeout - {e}"}
        except Exception as e:
            # Catch any other unexpected errors
            print(f"An unexpected error occurred: {e}")
            return {"subject": "Error", "body": f"Failed to generate email: An unexpected error occurred - {e}"}