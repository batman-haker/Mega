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


class Config:
    """Centralna konfiguracja aplikacji STOCKANALYZER"""

    # ============================================
    # PATHS
    # ============================================
    BASE_DIR = BASE_DIR
    DATABASE_PATH = BASE_DIR / 'stockanalyzer.db'
    EXPORTS_DIR = BASE_DIR / 'exports'
    STATIC_DIR = BASE_DIR / 'static'

    # External project paths
    FRED_PROJECT_PATH = Path(os.getenv('FRED_PROJECT_PATH', 'C:\\FRED'))
    XSCRAP_CACHE_PATH = Path(os.getenv('XSCRAP_CACHE_PATH', 'C:\\Xscrap\\x-financial-analyzer\\data\\cache'))

    # ============================================
    # API KEYS
    # ============================================
    FRED_API_KEY = os.getenv('FRED_API_KEY', '')
    GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY', '')
    ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY', '')

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

        # Check API Keys
        if not cls.FRED_API_KEY:
            errors['FRED_API_KEY'] = 'Brak FRED_API_KEY w pliku .env'

        if not cls.GOOGLE_API_KEY:
            errors['GOOGLE_API_KEY'] = 'Brak GOOGLE_API_KEY w pliku .env'

        # Check external paths
        if not cls.FRED_PROJECT_PATH.exists():
            errors['FRED_PROJECT_PATH'] = f'Katalog FRED nie istnieje: {cls.FRED_PROJECT_PATH}'

        if not cls.XSCRAP_CACHE_PATH.exists():
            errors['XSCRAP_CACHE_PATH'] = f'Katalog Xscrap cache nie istnieje: {cls.XSCRAP_CACHE_PATH}'

        # Ensure exports directory exists
        cls.EXPORTS_DIR.mkdir(exist_ok=True)

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
