"""
Test which API key is actually being loaded
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Force reload .env
env_path = Path('stockanalyzer/.env')
print(f"Loading from: {env_path.absolute()}")
print(f"File exists: {env_path.exists()}")

# Clear any existing env vars
if 'GOOGLE_API_KEY' in os.environ:
    del os.environ['GOOGLE_API_KEY']

# Load fresh
load_dotenv(env_path, override=True)

api_key = os.getenv('GOOGLE_API_KEY')

print("\n" + "="*60)
print("LOADED API KEY:")
print("="*60)
print(f"First 30 chars: {api_key[:30] if api_key else 'NONE'}...")
print(f"Last 10 chars: ...{api_key[-10:] if api_key else 'NONE'}")
print(f"Full length: {len(api_key) if api_key else 0} characters")
print("="*60)

# Also read file directly
print("\n" + "="*60)
print("DIRECT FILE READ:")
print("="*60)
with open(env_path, 'r') as f:
    for line in f:
        if 'GOOGLE_API_KEY' in line and not line.strip().startswith('#'):
            print(line.strip())
print("="*60)
