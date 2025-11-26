"""
MEGABOT Configuration
Centralized config for all data sources and AI APIs
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Main configuration class"""

    # === PROJECT PATHS ===
    BASE_DIR = Path(__file__).parent.parent
    DATA_DIR = BASE_DIR / "data"
    LOGS_DIR = BASE_DIR / "logs"

    # === EXTERNAL PROJECTS PATHS ===
    FRED_DIR = Path(r"C:\FRED")
    OPENBB_DIR = Path(r"C:\openBB")
    XSCRAP_DIR = Path(r"C:\Xscrap\x-financial-analyzer")

    # Twitter data paths
    TWITTER_DATA_DIR = XSCRAP_DIR / "data" / "cache"
    TWITTER_RAW_DIR = XSCRAP_DIR / "data" / "raw"

    # === API KEYS ===

    # FRED (Macro data)
    FRED_API_KEY = os.getenv('FRED_API_KEY')

    # AI APIs
    ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')  # Claude
    GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')  # Gemini

    # OpenAI (backup/optional)
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

    # === AI MODEL SETTINGS ===
    DEFAULT_AI_PROVIDER = "gemini"  # "claude" or "gemini"

    CLAUDE_MODEL = "claude-3-5-sonnet-20241022"  # Latest Sonnet
    GEMINI_MODEL = "gemini-1.5-flash"  # Gemini 1.5 Flash (szybki i darmowy)

    MAX_TOKENS = 4096
    TEMPERATURE = 0.3  # Conservative for financial advice

    # === DATA COLLECTION SETTINGS ===

    # FRED indicators to collect
    FRED_INDICATORS = [
        'reserves', 'tga', 'reverse_repo', 'fed_balance',
        'sofr', 'iorb', 'effr',
        'm2', 'yield_curve', 'vix', 'fin_conditions',
        'dollar_index', 'hy_spread'
    ]

    # Twitter experts to analyze (usernames)
    TWITTER_EXPERTS = [
        'Dan_Kostecki',      # Main liquidity expert
        'T_Smolarek',        # Macro
        'hedgefundowiec',    # Hedge fund perspective
        'rditrych',          # Markets
        'ksochanek',         # Analysis
        'HayekAndKeynes',    # Macro theory
    ]

    # Stock data settings
    DEFAULT_STOCK_PERIOD = "3mo"  # yfinance period
    DEFAULT_STOCK_INTERVAL = "1d"

    # === SCORING WEIGHTS ===
    # How much each signal contributes to final score
    WEIGHTS = {
        'fred_liquidity': 0.40,   # 40% - macro environment
        'stock_technicals': 0.35,  # 35% - stock fundamentals/technicals
        'twitter_sentiment': 0.25, # 25% - expert sentiment
    }

    # === CACHE SETTINGS ===
    CACHE_TWITTER_MINUTES = 30  # How long to cache Twitter data
    CACHE_FRED_MINUTES = 60     # FRED updates daily
    CACHE_STOCK_MINUTES = 5     # Stock data - more frequent

    # === ALERTS ===
    ALERT_THRESHOLD_BUY = 70   # Score >= 70 = strong buy
    ALERT_THRESHOLD_SELL = 30  # Score <= 30 = strong sell

    # === LOGGING ===
    LOG_LEVEL = "INFO"
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

    @classmethod
    def validate(cls):
        """Validate that all required configs are set"""
        errors = []

        # Check API keys
        if not cls.FRED_API_KEY:
            errors.append("[X] FRED_API_KEY not set")

        if not cls.ANTHROPIC_API_KEY and not cls.GOOGLE_API_KEY:
            errors.append("[X] Neither ANTHROPIC_API_KEY nor GOOGLE_API_KEY set (need at least one)")

        # Check paths
        if not cls.FRED_DIR.exists():
            errors.append(f"[X] FRED directory not found: {cls.FRED_DIR}")

        if not cls.OPENBB_DIR.exists():
            errors.append(f"[X] OpenBB directory not found: {cls.OPENBB_DIR}")

        if not cls.XSCRAP_DIR.exists():
            errors.append(f"[X] Xscrap directory not found: {cls.XSCRAP_DIR}")

        if errors:
            print("\n[!] CONFIGURATION ERRORS:\n")
            for error in errors:
                print(f"  {error}")
            print("\n[i] Fix these in your .env file!\n")
            return False

        print("[OK] Configuration validated successfully!")
        return True

    @classmethod
    def get_ai_config(cls):
        """Get AI provider configuration"""
        if cls.DEFAULT_AI_PROVIDER == "claude":
            return {
                'provider': 'claude',
                'api_key': cls.ANTHROPIC_API_KEY,
                'model': cls.CLAUDE_MODEL,
                'max_tokens': cls.MAX_TOKENS,
                'temperature': cls.TEMPERATURE,
            }
        elif cls.DEFAULT_AI_PROVIDER == "gemini":
            return {
                'provider': 'gemini',
                'api_key': cls.GOOGLE_API_KEY,
                'model': cls.GEMINI_MODEL,
                'max_tokens': cls.MAX_TOKENS,
                'temperature': cls.TEMPERATURE,
            }
        else:
            raise ValueError(f"Unknown AI provider: {cls.DEFAULT_AI_PROVIDER}")


# Create directories if they don't exist
Config.DATA_DIR.mkdir(exist_ok=True)
Config.LOGS_DIR.mkdir(exist_ok=True)


if __name__ == "__main__":
    # Test configuration
    print("="*60)
    print("MEGABOT Configuration Test")
    print("="*60)
    Config.validate()
    print("\nAI Config:", Config.get_ai_config())
    print("\nPaths:")
    print(f"  FRED: {Config.FRED_DIR}")
    print(f"  OpenBB: {Config.OPENBB_DIR}")
    print(f"  Xscrap: {Config.XSCRAP_DIR}")
    print(f"  Twitter Data: {Config.TWITTER_DATA_DIR}")
