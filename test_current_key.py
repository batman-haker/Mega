"""
Test API key from .env file
"""
import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load from stockanalyzer/.env
load_dotenv('stockanalyzer/.env')

api_key = os.getenv('GOOGLE_API_KEY')
print(f"Testing with key from .env: {api_key[:30]}...")

genai.configure(api_key=api_key)

print("\n" + "="*60)
print("TESTING GEMINI 2.5 FLASH")
print("="*60)

try:
    model = genai.GenerativeModel('gemini-2.5-flash')

    response = model.generate_content("Say 'API works!' in one sentence.")

    print(f"\n[SUCCESS]")
    print(response.text)
    print("\n" + "="*60)
    print("API KEY FROM .ENV IS VALID!")
    print("="*60)

except Exception as e:
    print(f"\n[ERROR] {e}")
    print("\n" + "="*60)
    print("API KEY FAILED")
    print("="*60)
