import os
from dotenv import load_dotenv

load_dotenv()

print("OpenAI Key:", os.getenv("OPENAI_API_KEY"))
print("Gmail User:", os.getenv("GMAIL_USER"))
print("Gmail App Password:", os.getenv("GMAIL_APP_PASSWORD"))
