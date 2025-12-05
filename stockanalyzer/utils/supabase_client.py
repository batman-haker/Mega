"""
Supabase Client for STOCKANALYZER
Handles cloud database operations for game saves, analysis history, and more.
"""

import os
from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path
from supabase import create_client, Client
from dotenv import load_dotenv, find_dotenv

# Load environment variables (search upwards from current directory)
dotenv_path = find_dotenv()
if dotenv_path:
    load_dotenv(dotenv_path)
else:
    # Fallback: look in parent directories
    current_dir = Path(__file__).resolve().parent
    for _ in range(3):  # Search up to 3 levels
        env_file = current_dir / '.env'
        if env_file.exists():
            load_dotenv(env_file)
            break
        current_dir = current_dir.parent

# Supabase configuration
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Initialize Supabase client
supabase: Client = None

def get_supabase_client() -> Client:
    """
    Get or create Supabase client singleton.

    Returns:
        Client: Supabase client instance
    """
    global supabase

    if supabase is None:
        if not SUPABASE_URL or not SUPABASE_KEY:
            raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in .env file")

        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

    return supabase


# ============================================
# GAME SAVES
# ============================================

def save_game(
    user_id: str,
    save_name: str,
    scenario_name: str,
    game_state: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Save game state to Supabase.

    Args:
        user_id: User identifier (email or session ID)
        save_name: Name of the save (e.g., "Moja gra 1929")
        scenario_name: Scenario name (e.g., "great_depression")
        game_state: Game state dictionary containing:
            - cash: float
            - portfolio: Dict[str, int] {ticker: shares}
            - current_date: str
            - events_seen: List[str]
            - decisions: List[Dict]

    Returns:
        Dict with saved game data including ID
    """
    client = get_supabase_client()

    data = {
        "user_id": user_id,
        "save_name": save_name,
        "scenario_name": scenario_name,
        "game_state": game_state,
        "updated_at": datetime.now().isoformat()
    }

    try:
        result = client.table("game_saves").insert(data).execute()
        return result.data[0] if result.data else {}
    except Exception as e:
        print(f"Error saving game: {e}")
        return {"error": str(e)}


def load_game(save_id: str) -> Optional[Dict[str, Any]]:
    """
    Load game save by ID.

    Args:
        save_id: UUID of the save

    Returns:
        Game save data or None if not found
    """
    client = get_supabase_client()

    try:
        result = client.table("game_saves").select("*").eq("id", save_id).execute()
        return result.data[0] if result.data else None
    except Exception as e:
        print(f"Error loading game: {e}")
        return None


def list_user_saves(user_id: str, limit: int = 20) -> List[Dict[str, Any]]:
    """
    List all saves for a user.

    Args:
        user_id: User identifier
        limit: Maximum number of saves to return

    Returns:
        List of save records
    """
    client = get_supabase_client()

    try:
        result = (
            client.table("game_saves")
            .select("id, save_name, scenario_name, created_at, updated_at")
            .eq("user_id", user_id)
            .order("updated_at", desc=True)
            .limit(limit)
            .execute()
        )
        return result.data if result.data else []
    except Exception as e:
        print(f"Error listing saves: {e}")
        return []


def delete_save(save_id: str) -> bool:
    """
    Delete a game save.

    Args:
        save_id: UUID of the save

    Returns:
        True if deleted successfully
    """
    client = get_supabase_client()

    try:
        client.table("game_saves").delete().eq("id", save_id).execute()
        return True
    except Exception as e:
        print(f"Error deleting save: {e}")
        return False


# ============================================
# ANALYSIS HISTORY
# ============================================

def save_analysis(
    user_id: str,
    ticker: str,
    experts_used: List[str],
    verdicts: Dict[str, str],
    market_data: Dict[str, Any],
    macro_data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Save AI analysis to history.

    Args:
        user_id: User identifier
        ticker: Stock ticker
        experts_used: List of expert names
        verdicts: Dict mapping expert name to verdict
        market_data: Market data snapshot
        macro_data: Macro data snapshot

    Returns:
        Saved analysis record
    """
    client = get_supabase_client()

    data = {
        "user_id": user_id,
        "ticker": ticker,
        "experts_used": experts_used,
        "verdicts": verdicts,
        "market_data": market_data,
        "macro_data": macro_data
    }

    try:
        result = client.table("analysis_history").insert(data).execute()
        return result.data[0] if result.data else {}
    except Exception as e:
        print(f"Error saving analysis: {e}")
        return {"error": str(e)}


def get_user_analysis_history(
    user_id: str,
    limit: int = 10
) -> List[Dict[str, Any]]:
    """
    Get user's analysis history.

    Args:
        user_id: User identifier
        limit: Number of records to return

    Returns:
        List of analysis records
    """
    client = get_supabase_client()

    try:
        result = (
            client.table("analysis_history")
            .select("*")
            .eq("user_id", user_id)
            .order("created_at", desc=True)
            .limit(limit)
            .execute()
        )
        return result.data if result.data else []
    except Exception as e:
        print(f"Error getting analysis history: {e}")
        return []


# ============================================
# WATCHLISTS
# ============================================

def add_to_watchlist(
    user_id: str,
    ticker: str,
    notes: Optional[str] = None,
    target_price: Optional[float] = None
) -> Dict[str, Any]:
    """
    Add stock to watchlist.

    Args:
        user_id: User identifier
        ticker: Stock ticker
        notes: Optional notes
        target_price: Optional target price

    Returns:
        Watchlist entry
    """
    client = get_supabase_client()

    data = {
        "user_id": user_id,
        "ticker": ticker,
        "notes": notes,
        "target_price": target_price
    }

    try:
        result = client.table("watchlists").insert(data).execute()
        return result.data[0] if result.data else {}
    except Exception as e:
        print(f"Error adding to watchlist: {e}")
        return {"error": str(e)}


def get_watchlist(user_id: str) -> List[Dict[str, Any]]:
    """
    Get user's watchlist.

    Args:
        user_id: User identifier

    Returns:
        List of watchlist entries
    """
    client = get_supabase_client()

    try:
        result = (
            client.table("watchlists")
            .select("*")
            .eq("user_id", user_id)
            .order("added_at", desc=True)
            .execute()
        )
        return result.data if result.data else []
    except Exception as e:
        print(f"Error getting watchlist: {e}")
        return []


def remove_from_watchlist(user_id: str, ticker: str) -> bool:
    """
    Remove stock from watchlist.

    Args:
        user_id: User identifier
        ticker: Stock ticker

    Returns:
        True if removed successfully
    """
    client = get_supabase_client()

    try:
        client.table("watchlists").delete().eq("user_id", user_id).eq("ticker", ticker).execute()
        return True
    except Exception as e:
        print(f"Error removing from watchlist: {e}")
        return False


# ============================================
# PORTFOLIOS
# ============================================

def save_portfolio(
    user_id: str,
    name: str,
    holdings: List[Dict[str, Any]],
    is_virtual: bool = True
) -> Dict[str, Any]:
    """
    Save or update portfolio.

    Args:
        user_id: User identifier
        name: Portfolio name
        holdings: List of holdings [{"ticker": str, "shares": int, "avg_price": float, "date_bought": str}]
        is_virtual: Whether this is a virtual (paper) portfolio

    Returns:
        Saved portfolio record
    """
    client = get_supabase_client()

    data = {
        "user_id": user_id,
        "name": name,
        "holdings": holdings,
        "is_virtual": is_virtual,
        "updated_at": datetime.now().isoformat()
    }

    try:
        result = client.table("portfolios").insert(data).execute()
        return result.data[0] if result.data else {}
    except Exception as e:
        print(f"Error saving portfolio: {e}")
        return {"error": str(e)}


def get_user_portfolios(user_id: str) -> List[Dict[str, Any]]:
    """
    Get user's portfolios.

    Args:
        user_id: User identifier

    Returns:
        List of portfolio records
    """
    client = get_supabase_client()

    try:
        result = (
            client.table("portfolios")
            .select("*")
            .eq("user_id", user_id)
            .order("updated_at", desc=True)
            .execute()
        )
        return result.data if result.data else []
    except Exception as e:
        print(f"Error getting portfolios: {e}")
        return []


# ============================================
# UTILITY FUNCTIONS
# ============================================

def test_connection() -> bool:
    """
    Test Supabase connection.

    Returns:
        True if connection successful
    """
    try:
        client = get_supabase_client()
        # Try to select from game_saves table
        result = client.table("game_saves").select("id").limit(1).execute()
        return True
    except Exception as e:
        print(f"Connection test failed: {e}")
        return False
