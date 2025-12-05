"""
Quick test script for Supabase connection
"""

import sys
import os
sys.path.insert(0, 'stockanalyzer')

# Load .env FIRST
from dotenv import load_dotenv
load_dotenv()

# Debug: check env before import
print("[DEBUG] After load_dotenv():")
print(f"  SUPABASE_URL: {os.getenv('SUPABASE_URL')}")
print(f"  SUPABASE_KEY: {os.getenv('SUPABASE_KEY')[:20] if os.getenv('SUPABASE_KEY') else None}")

from utils.supabase_client import test_connection, save_game, list_user_saves, SUPABASE_URL, SUPABASE_KEY

# Debug: check after import
print("\n[DEBUG] After import:")
print(f"  SUPABASE_URL: {SUPABASE_URL}")
print(f"  SUPABASE_KEY: {SUPABASE_KEY[:20] if SUPABASE_KEY else None}")

print("\n[*] Testing Supabase connection...")

if test_connection():
    print("[OK] Connection successful!")

    # Test saving a game
    print("\n[*] Testing game save...")
    result = save_game(
        user_id="test_user",
        save_name="Test Save",
        scenario_name="great_depression",
        game_state={
            "cash": 10000.0,
            "portfolio": {"AAPL": 10},
            "current_date": "1929-10-24",
            "events_seen": ["crash"],
            "decisions": []
        }
    )

    if "error" not in result:
        print(f"[OK] Game saved! ID: {result.get('id')}")

        # Test listing saves
        print("\n[*] Testing list saves...")
        saves = list_user_saves("test_user")
        print(f"[OK] Found {len(saves)} saves:")
        for save in saves:
            print(f"   - {save['save_name']} ({save['scenario_name']})")
    else:
        print(f"[ERROR] {result['error']}")

else:
    print("[ERROR] Connection failed!")
    print("Check:")
    print("  1. .env file has SUPABASE_URL and SUPABASE_KEY")
    print("  2. Supabase tables are created (run SQL from earlier)")
    print("  3. RLS policies allow operations")
