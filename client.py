import google.generativeai as genai
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv("GEMINIAI_API_KEY")

if not api_key:
    raise ValueError("❌ GEMINIAI_API_KEY not found. Please check your .env file.")


genai.configure(api_key=api_key)


model = genai.GenerativeModel("gemini-1.5-flash")


prompt = """You are a virtual assistant named Alexa skilled in general tasks like Alexa and Google Cloud.
User: What is coding?
"""

response = model.generate_content(prompt)

print(response.text)