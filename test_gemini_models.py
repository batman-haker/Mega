"""
Test Gemini API - List available models
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
print("AVAILABLE GEMINI MODELS")
print("="*60)

try:
    models = genai.list_models()

    for model in models:
        if 'generateContent' in model.supported_generation_methods:
            print(f"\n[OK] {model.name}")
            print(f"   Display: {model.display_name}")
            print(f"   Methods: {', '.join(model.supported_generation_methods)}")

except Exception as e:
    print(f"ERROR: {e}")

print("\n" + "="*60)
