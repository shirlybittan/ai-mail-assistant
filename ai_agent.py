# ai_agent.py
import os
import json
import re # Added for regex
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, SystemMessage

# Import from config.py
from config import OPENAI_API_KEY

class SmartEmailAgent:
    def __init__(self):
        # Initialize the LLM with API key from config
        self.llm = ChatOpenAI(model="gpt-4o", temperature=0.7, openai_api_key=OPENAI_API_KEY)

    def generate_email_preview(self, user_instruction: str, contact_info: dict) -> dict:
        """
        Generates email content (subject and body) for a single contact,
        based on a user prompt, without actually sending.
        Returns a dictionary with 'email_subject', 'email_body', and 'raw_llm_output'.
        """
        # Improved SystemMessage for better control over AI output
        system_message_content = """You are a helpful and creative AI assistant specializing in crafting professional and personalized emails. Your task is to generate an email subject and body for a given contact, based on a user's instruction.
            You must provide the output in a JSON format with keys 'email_subject' and 'email_body'.
            Always personalize the email using information from `contact_info` (e.g., their 'name', 'company', 'product', etc.).
            Ensure the email is friendly, informative, and persuasive as per the user's instruction.
            Keep the email body concise, ideally under 150 words, unless explicitly asked for more detail.
            """

        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content=system_message_content),
            HumanMessage(content=f"""
            User instruction: {user_instruction}

            Contact Information:
            {json.dumps(contact_info, indent=2)}

            Generate the email content in JSON format:
            """) # Removed the example JSON block in the prompt, relying on SystemMessage
                 # and robust parsing to handle it. LLMs are good at inferring format.
        ])

        try:
            chain = prompt | self.llm
            response = chain.invoke({"user_instruction": user_instruction, "contact_info": contact_info})
            content_str = response.content.strip()

            try:
                # Robust JSON extraction using regex
                json_match = re.search(r"{[\s\S]*}", content_str)
                parsed_content = {}
                if json_match:
                    json_content = json_match.group(0)
                    parsed_content = json.loads(json_content)
                else:
                    raise json.JSONDecodeError("No JSON object found in LLM response", content_str, 0)

                return {
                    "email_subject": parsed_content.get("email_subject", ""),
                    "email_body": parsed_content.get("email_body", ""),
                    "raw_llm_output": content_str # For debugging
                }
            except json.JSONDecodeError as jde:
                return {
                    "email_subject": "", "email_body": "",
                    "raw_llm_output": f"LLM did not return valid JSON or was unparsable: {jde}\nRaw Output:\n{content_str}"
                }

        except Exception as e:
            return {
                "email_subject": "", "email_body": "",
                "raw_llm_output": f"Error during LLM invocation: {e}"
            }

if __name__ == '__main__':
    # --- For Testing: Test the AI agent's email generation ---
    agent = SmartEmailAgent()
    
    sample_contact = {
        'name': 'John Doe',
        'email': 'john.doe@example.com',
        'company': 'Acme Corp',
        'product': 'Ultimate Widget',
        'last_interaction': '2025-06-01'
    }
    user_instruction = "Craft a follow-up email after their purchase of the {{product}}. Thank them, offer support, and subtly suggest an upgrade."

    print("--- Testing Agent Preview ---")
    preview = agent.generate_email_preview(user_instruction, sample_contact)
    print("Email Subject Preview:", preview.get('email_subject'))
    print("Email Body Preview:", preview.get('email_body'))
    print("Raw LLM Output (for debug):", preview.get('raw_llm_output'))