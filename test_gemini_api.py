"""
Quick test of Gemini API with new key
"""
import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load .env
load_dotenv('stockanalyzer/.env')

# Configure API
api_key = os.getenv('GOOGLE_API_KEY')
print(f"Using API Key: {api_key[:20]}...")

genai.configure(api_key=api_key)

print("\n" + "="*60)
print("TESTING GEMINI API")
print("="*60)

try:
    # Test with gemini-2.5-flash
    model = genai.GenerativeModel('gemini-2.5-flash')

    prompt = "Hello! Can you briefly introduce yourself in one sentence?"

    print(f"\nSending prompt: {prompt}")
    print("Waiting for response...")

    response = model.generate_content(prompt)

    print(f"\n[SUCCESS] Response:")
    print(response.text)

    print("\n" + "="*60)
    print("API TEST PASSED!")
    print("="*60)

except Exception as e:
    print(f"\n[ERROR] API Test Failed: {e}")
    import traceback
    traceback.print_exc()
    print("\n" + "="*60)
