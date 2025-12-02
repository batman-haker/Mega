"""
Direct test with new API key
"""
import google.generativeai as genai

# New API key directly
api_key = "AIzaSyBWFbOzAG6BFctbZ1zVQ027STdpDOxWR8I"

print(f"Testing with key: {api_key[:20]}...")

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
    print("API KEY IS VALID!")
    print("="*60)

except Exception as e:
    print(f"\n[ERROR] {e}")
    print("\n" + "="*60)
