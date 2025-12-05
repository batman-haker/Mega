"""
Create Supabase tables via API
"""

import sys
sys.path.insert(0, 'stockanalyzer')

from dotenv import load_dotenv
load_dotenv()

from utils.supabase_client import get_supabase_client

print("[*] Connecting to Supabase...")
client = get_supabase_client()

# SQL to create all tables
sql = """
-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 1. GAME SAVES TABLE
CREATE TABLE IF NOT EXISTS game_saves (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id TEXT NOT NULL,
    save_name TEXT NOT NULL,
    scenario_name TEXT NOT NULL,
    game_state JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_game_saves_user_id ON game_saves(user_id);
CREATE INDEX IF NOT EXISTS idx_game_saves_created_at ON game_saves(created_at DESC);

-- 2. ANALYSIS HISTORY TABLE
CREATE TABLE IF NOT EXISTS analysis_history (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id TEXT NOT NULL,
    ticker TEXT NOT NULL,
    experts_used TEXT[],
    verdicts JSONB,
    market_data JSONB,
    macro_data JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_analysis_history_user_id ON analysis_history(user_id);
CREATE INDEX IF NOT EXISTS idx_analysis_history_ticker ON analysis_history(ticker);
CREATE INDEX IF NOT EXISTS idx_analysis_history_created_at ON analysis_history(created_at DESC);

-- 3. WATCHLISTS TABLE
CREATE TABLE IF NOT EXISTS watchlists (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id TEXT NOT NULL,
    ticker TEXT NOT NULL,
    notes TEXT,
    target_price NUMERIC,
    added_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_watchlists_user_id ON watchlists(user_id);

-- 4. PORTFOLIOS TABLE
CREATE TABLE IF NOT EXISTS portfolios (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id TEXT NOT NULL,
    name TEXT NOT NULL,
    holdings JSONB NOT NULL,
    is_virtual BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_portfolios_user_id ON portfolios(user_id);

-- Enable Row Level Security
ALTER TABLE game_saves ENABLE ROW LEVEL SECURITY;
ALTER TABLE analysis_history ENABLE ROW LEVEL SECURITY;
ALTER TABLE watchlists ENABLE ROW LEVEL SECURITY;
ALTER TABLE portfolios ENABLE ROW LEVEL SECURITY;
"""

print("[*] Creating tables...")
print("    This may take a moment...")

try:
    # Execute SQL using rpc (Supabase functions)
    # Note: We need to use the PostgREST API directly
    result = client.rpc('exec_sql', {'query': sql}).execute()
    print("[OK] Tables created successfully!")

except Exception as e:
    print(f"[INFO] Using alternative method...")
    # Alternative: Create tables one by one using table() API
    # This won't work for CREATE TABLE, so we'll just inform user
    print(f"[ERROR] Cannot create tables via Python API")
    print(f"Error: {e}")
    print("")
    print("[ACTION REQUIRED] Please create tables manually:")
    print("1. Go to: https://supabase.com/dashboard/project/vblmscpszrifwpwtaxtx/editor")
    print("2. Click 'SQL Editor' in left menu")
    print("3. Click 'New query'")
    print("4. Copy the SQL from earlier message")
    print("5. Click RUN")
    sys.exit(1)

print("")
print("[*] Verifying tables...")
try:
    # Try to query game_saves table
    result = client.table("game_saves").select("id").limit(1).execute()
    print("[OK] game_saves table exists!")

    result = client.table("analysis_history").select("id").limit(1).execute()
    print("[OK] analysis_history table exists!")

    result = client.table("watchlists").select("id").limit(1).execute()
    print("[OK] watchlists table exists!")

    result = client.table("portfolios").select("id").limit(1).execute()
    print("[OK] portfolios table exists!")

    print("")
    print("[SUCCESS] All tables created and verified!")

except Exception as e:
    print(f"[ERROR] Verification failed: {e}")
    print("")
    print("Tables might not be created. Please use manual method.")
