"""
STOCKANALYZER - Configuration Management

Ten moduł zarządza konfiguracją aplikacji:
- Ładowanie zmiennych środowiskowych z .env
- Walidacja API keys
- Walidacja ścieżek do zewnętrznych projektów
- Stałe konfiguracyjne

Użycie:
    from utils.config import Config

    config = Config()
    if config.validate():
        print(f"FRED API Key: {config.FRED_API_KEY}")
"""

import os
import sys
from pathlib import Path
from typing import Dict, Tuple
from dotenv import load_dotenv

# Ładowanie .env z katalogu stockanalyzer
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / '.env', override=True)

# Try to import streamlit for cloud secrets support
try:
    import streamlit as st
    _STREAMLIT_AVAILABLE = True
except ImportError:
    _STREAMLIT_AVAILABLE = False


def _get_secret(key: str, default: str = '', secrets_path: str = None) -> str:
    """
    Get secret from Streamlit secrets (cloud) or environment variable (local)

    Priority:
    1. Streamlit secrets (for cloud deployment)
    2. Environment variable (for local development)
    3. Default value

    Args:
        key: Key name (e.g., 'GOOGLE_API_KEY')
        default: Default value if not found
        secrets_path: Path in st.secrets (e.g., 'gemini.api_key')
    """
    # Try Streamlit secrets first (for cloud)
    if _STREAMLIT_AVAILABLE and hasattr(st, 'secrets'):
        try:
            if secrets_path:
                # Navigate nested path (e.g., 'gemini.api_key')
                parts = secrets_path.split('.')
                value = st.secrets
                for part in parts:
                    value = value[part]
                if value:
                    return value
            # Try direct key
            if key in st.secrets:
                return st.secrets[key]
        except (KeyError, AttributeError):
            pass

    # Fall back to environment variable
    return os.getenv(key, default)


class Config:
    """Centralna konfiguracja aplikacji STOCKANALYZER"""

    # ============================================
    # PATHS
    # ============================================
    BASE_DIR = BASE_DIR
    DATABASE_PATH = BASE_DIR / 'stockanalyzer.db'
    EXPORTS_DIR = BASE_DIR / 'exports'
    STATIC_DIR = BASE_DIR / 'static'

    # External project paths (optional, only for local dev)
    FRED_PROJECT_PATH = Path(os.getenv('FRED_PROJECT_PATH', 'C:\\FRED'))
    XSCRAP_CACHE_PATH = Path(os.getenv('XSCRAP_CACHE_PATH', 'C:\\Xscrap\\x-financial-analyzer\\data\\cache'))

    # ============================================
    # API KEYS (supports both st.secrets and .env)
    # ============================================
    FRED_API_KEY = _get_secret('FRED_API_KEY', secrets_path='fred.api_key')
    GOOGLE_API_KEY = _get_secret('GOOGLE_API_KEY', secrets_path='gemini.api_key')
    ANTHROPIC_API_KEY = _get_secret('ANTHROPIC_API_KEY', secrets_path='anthropic.api_key')

    # ============================================
    # AI SETTINGS
    # ============================================
    DEFAULT_AI_MODEL = os.getenv('DEFAULT_AI_MODEL', 'gemini-1.5-flash')
    AI_TEMPERATURE = 0.3  # Conservative dla financial advice
    AI_MAX_TOKENS = 4096
    GEMINI_RATE_LIMIT_SEC = 20  # 20 sekund między zapytaniami (free tier)

    # ============================================
    # CACHE SETTINGS (TTL in seconds)
    # ============================================
    FRED_CACHE_TTL = int(os.getenv('FRED_CACHE_TTL', 3600))      # 1 godzina
    STOCK_CACHE_TTL = int(os.getenv('STOCK_CACHE_TTL', 900))     # 15 minut
    TWITTER_CACHE_TTL = int(os.getenv('TWITTER_CACHE_TTL', 1800)) # 30 minut
    ANALYSIS_FRESH_TTL = 3600  # Analiza jest "świeża" przez 1h

    # ============================================
    # DATA COLLECTION SETTINGS
    # ============================================
    STOCK_HISTORY_PERIOD = '3mo'  # 3 miesiące historii
    STOCK_HISTORY_INTERVAL = '1d'  # Dane dzienne
    TWITTER_MAX_AGE_HOURS = 24     # Tweety z ostatnich 24h

    # ============================================
    # SCORING WEIGHTS
    # ============================================
    WEIGHTS = {
        'fred_liquidity': 0.40,    # 40% - Makro environment
        'stock_analysis': 0.35,    # 35% - Stock fundamentals + technicals
        'twitter_sentiment': 0.25,  # 25% - Expert sentiment
    }

    # ============================================
    # EXPERT TWITTER ACCOUNTS
    # ============================================
    TWITTER_EXPERTS = [
        'Dan_Kostecki',      # Liquidity expert
        'T_Smolarek',        # Macro
        'hedgefundowiec',    # Hedge fund perspective
        'rditrych',          # Markets
        'ksochanek',         # Analysis
        'HayekAndKeynes',    # Macro theory
    ]

    # ============================================
    # SUPPORTED EXCHANGES (dla ticker search)
    # ============================================
    SUPPORTED_EXCHANGES = ['NYSE', 'NASDAQ', 'GPW']

    # ============================================
    # SCORE THRESHOLDS
    # ============================================
    THRESHOLDS = {
        'STRONG_BUY': 70,
        'BUY': 30,
        'HOLD': -30,
        'SELL': -70,
        # Below -70 = STRONG_SELL
    }

    # ============================================
    # APPLICATION SETTINGS
    # ============================================
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LANGUAGE = os.getenv('LANGUAGE', 'pl')

    # ============================================
    # CYBERPUNK THEME COLORS
    # ============================================
    COLORS = {
        'bg_dark': '#0a0e27',
        'bg_card': '#1a1a2e',
        'neon_cyan': '#00f5ff',
        'neon_magenta': '#ff006e',
        'neon_green': '#39ff14',
        'neon_red': '#ff073a',
        'neon_yellow': '#ffed4e',
        'text_primary': '#e0e0e0',
    }

    # ============================================
    # VALIDATION
    # ============================================

    @classmethod
    def validate(cls) -> Tuple[bool, Dict[str, str]]:
        """
        Waliduje konfigurację aplikacji.

        Returns:
            Tuple[bool, Dict]: (is_valid, errors)
                - is_valid: True jeśli wszystko OK
                - errors: Dict z błędami {'key': 'error_message'}

        Example:
            >>> is_valid, errors = Config.validate()
            >>> if not is_valid:
            >>>     print(f"Błędy konfiguracji: {errors}")
        """
        errors = {}

        # Check API Keys (critical for both local and cloud)
        if not cls.GOOGLE_API_KEY:
            errors['GOOGLE_API_KEY'] = 'Brak GOOGLE_API_KEY (sprawdź .env lub Streamlit secrets)'

        # FRED API is optional - some features may not work without it
        if not cls.FRED_API_KEY:
            # Just a warning, not a blocker
            pass

        # Check external paths (only for local development)
        # In cloud deployment, these paths don't exist and that's OK
        is_cloud = _STREAMLIT_AVAILABLE and hasattr(st, 'secrets') and len(st.secrets) > 0

        if not is_cloud:
            # Only validate paths in local environment
            if not cls.FRED_PROJECT_PATH.exists():
                errors['FRED_PROJECT_PATH'] = f'Katalog FRED nie istnieje: {cls.FRED_PROJECT_PATH} (tylko local)'

            if not cls.XSCRAP_CACHE_PATH.exists():
                errors['XSCRAP_CACHE_PATH'] = f'Katalog Xscrap cache nie istnieje: {cls.XSCRAP_CACHE_PATH} (tylko local)'

        # Ensure exports directory exists
        try:
            cls.EXPORTS_DIR.mkdir(exist_ok=True, parents=True)
        except Exception as e:
            errors['EXPORTS_DIR'] = f'Nie można utworzyć katalogu exports: {e}'

        is_valid = len(errors) == 0
        return is_valid, errors

    @classmethod
    def print_config(cls):
        """Wyświetla aktualną konfigurację (bez API keys)"""
        print("=" * 60)
        print("STOCKANALYZER - Configuration")
        print("=" * 60)
        print(f"Base Directory: {cls.BASE_DIR}")
        print(f"Database: {cls.DATABASE_PATH}")
        print(f"FRED Project: {cls.FRED_PROJECT_PATH}")
        print(f"Xscrap Cache: {cls.XSCRAP_CACHE_PATH}")
        print(f"\nAI Model: {cls.DEFAULT_AI_MODEL}")
        print(f"Language: {cls.LANGUAGE}")
        print(f"\nCache TTL:")
        print(f"  - FRED: {cls.FRED_CACHE_TTL}s")
        print(f"  - Stock: {cls.STOCK_CACHE_TTL}s")
        print(f"  - Twitter: {cls.TWITTER_CACHE_TTL}s")
        print(f"\nScoring Weights:")
        for key, weight in cls.WEIGHTS.items():
            print(f"  - {key}: {weight*100}%")
        print("=" * 60)


# ============================================
# AUTO-VALIDATION przy imporcie
# ============================================

if __name__ == "__main__":
    # Test konfiguracji
    Config.print_config()

    print("\nValidating configuration...")
    is_valid, errors = Config.validate()

    if is_valid:
        print("[OK] Konfiguracja jest poprawna!")
    else:
        print("[ERROR] Bledy konfiguracji:")
        for key, error in errors.items():
            print(f"  - {key}: {error}")
        sys.exit(1)
