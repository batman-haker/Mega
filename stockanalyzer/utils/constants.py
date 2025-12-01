"""
STOCKANALYZER - Constants & Configuration

Centralne miejsce dla wszystkich stałych używanych w projekcie:
- Twitter experts list
- Supported exchanges
- Scoring thresholds
- Recommendation levels
- Chart colors
- Keywords for sentiment analysis

Użycie:
    from utils.constants import TWITTER_EXPERTS, CHART_COLORS
"""

from typing import Dict, List

# ============================================
# TWITTER EXPERTS
# ============================================

TWITTER_EXPERTS: List[str] = [
    'Dan_Kostecki',      # Liquidity expert (#1)
    'T_Smolarek',        # Macro analysis
    'hedgefundowiec',    # Hedge fund perspective
    'rditrych',          # Markets
    'ksochanek',         # Technical analysis
    'HayekAndKeynes',    # Macro theory
]

# Expert descriptions (dla UI)
EXPERT_DESCRIPTIONS: Dict[str, str] = {
    'Dan_Kostecki': 'Ekspert płynności i FRED data',
    'T_Smolarek': 'Analiza makro i FED policy',
    'hedgefundowiec': 'Perspektywa hedge fund',
    'rditrych': 'Analiza rynków finansowych',
    'ksochanek': 'Analiza techniczna',
    'HayekAndKeynes': 'Teoria makroekonomiczna',
}


# ============================================
# SUPPORTED EXCHANGES
# ============================================

SUPPORTED_EXCHANGES: List[str] = [
    'NYSE',      # New York Stock Exchange
    'NASDAQ',    # NASDAQ
    'GPW',       # Giełda Papierów Wartościowych w Warszawie
]

# Exchange suffixes dla Yahoo Finance
EXCHANGE_SUFFIXES: Dict[str, str] = {
    'GPW': '.WA',      # Warsaw Stock Exchange
    'NYSE': '',        # No suffix needed
    'NASDAQ': '',      # No suffix needed
}


# ============================================
# SCORING THRESHOLDS
# ============================================

# Score range: -100 (very bearish) to +100 (very bullish)
SCORE_THRESHOLDS: Dict[str, int] = {
    'STRONG_BUY': 70,      # Score >= 70
    'BUY': 30,             # Score >= 30
    'HOLD': -30,           # Score >= -30
    'SELL': -70,           # Score >= -70
    # Below -70 = STRONG_SELL
}

# Recommendation levels (text labels)
RECOMMENDATION_LEVELS: List[str] = [
    'STRONG_BUY',
    'BUY',
    'HOLD',
    'SELL',
    'STRONG_SELL',
]


# ============================================
# MARKET REGIMES
# ============================================

MARKET_REGIMES: List[str] = [
    'RISK_ON',      # Bullish conditions
    'RISK_OFF',     # Cautious conditions
    'CRISIS',       # Crisis mode
    'UNKNOWN',      # Insufficient data
]

# Regime descriptions
REGIME_DESCRIPTIONS: Dict[str, str] = {
    'RISK_ON': 'Sprzyjające warunki - wysoka płynność, niski VIX',
    'RISK_OFF': 'Napięcia - obniżona płynność, rosnący VIX',
    'CRISIS': 'KRYZYS - krytyczne napięcia płynnościowe',
    'UNKNOWN': 'Brak wystarczających danych',
}

# Regime colors (dla UI)
REGIME_COLORS: Dict[str, str] = {
    'RISK_ON': '#39ff14',       # Neon green
    'RISK_OFF': '#ffed4e',      # Neon yellow
    'CRISIS': '#ff073a',        # Neon red
    'UNKNOWN': '#606060',       # Gray
}


# ============================================
# SENTIMENT KEYWORDS
# ============================================

# Bullish keywords (dla keyword-based sentiment)
BULLISH_KEYWORDS: List[str] = [
    # Polski
    'wzrost', 'rośnie', 'kupuj', 'kupować', 'buy', 'long',
    'bullish', 'bull', 'rally', 'breakout', 'silny', 'mocny',
    'zysk', 'wzrostowy', 'pozytywnie', 'dobrze',

    # Angielski
    'gain', 'up', 'strong', 'strength', 'outperform',
    'uptrend', 'higher', 'accumulate', 'opportunity',
]

# Bearish keywords
BEARISH_KEYWORDS: List[str] = [
    # Polski
    'spadek', 'spada', 'sprzedaj', 'sprzedawać', 'sell', 'short',
    'bearish', 'bear', 'crash', 'breakdown', 'słaby', 'spadkowy',
    'strata', 'negatywnie', 'źle', 'ryzyko',

    # Angielski
    'loss', 'down', 'weak', 'weakness', 'underperform',
    'downtrend', 'lower', 'distribute', 'danger', 'risk',
]


# ============================================
# CHART COLORS (Cyberpunk Theme)
# ============================================

CHART_COLORS: Dict[str, str] = {
    # Primary colors
    'background': 'rgba(26, 26, 46, 0.8)',
    'paper': 'rgba(10, 14, 39, 0.6)',
    'text': '#e0e0e0',

    # Line colors
    'line_up': '#39ff14',          # Neon green (upward trends)
    'line_down': '#ff073a',        # Neon red (downward trends)
    'line_neutral': '#00f5ff',     # Neon cyan (neutral)
    'line_secondary': '#ff006e',   # Neon magenta

    # Grid & axes
    'grid': 'rgba(0, 245, 255, 0.1)',
    'axis': 'rgba(0, 245, 255, 0.3)',
    'zero_line': 'rgba(0, 245, 255, 0.2)',

    # Candlestick colors
    'candle_up': '#39ff14',
    'candle_down': '#ff073a',
}


# ============================================
# DATA COLLECTION SETTINGS
# ============================================

# Stock data
STOCK_HISTORY_PERIOD: str = '3mo'        # 3 months
STOCK_HISTORY_INTERVAL: str = '1d'       # Daily data

# Twitter data
TWITTER_MAX_AGE_HOURS: int = 24          # Last 24 hours

# Technical indicators periods
MA_PERIODS: List[int] = [20, 50, 200]    # Moving averages
RSI_PERIOD: int = 14                      # RSI
MACD_FAST: int = 12                       # MACD fast
MACD_SLOW: int = 26                       # MACD slow
MACD_SIGNAL: int = 9                      # MACD signal


# ============================================
# AI PROMPTS TEMPLATES
# ============================================

# System prompt dla AI (używany w ai_service.py)
AI_SYSTEM_PROMPT: str = """Jesteś ekspertem finansowym z 20-letnim doświadczeniem w analizie rynków.
Specjalizujesz się w:
- Analizie makroekonomicznej (FRED, płynność, polityka monetarna)
- Analizie fundamentalnej spółek
- Analizie technicznej
- Ocenie ryzyka inwestycyjnego

Twoja analiza jest:
- Konkretna i oparta na danych
- Uczciwa (nie ukrywasz zagrożeń)
- Profesjonalna (bez emocji i hype'u)
- Polska (język polski)

Podajesz jasne rekomendacje: STRONG BUY, BUY, HOLD, SELL, STRONG_SELL.
"""

# Struktura pytań dla AI (używana w prompt_builder.py)
AI_QUESTIONS: List[str] = [
    "Czy powinienem kupić ten walor teraz?",
    "Jakie są główne argumenty ZA i PRZECIW?",
    "Jaki jest poziom ryzyka?",
    "Jaką strategię inwestycyjną rekomendujesz?",
    "Jakie są scenariusze (bull/base/bear case)?",
]


# ============================================
# FORMATTING HELPERS
# ============================================

def format_large_number(value: float) -> str:
    """
    Formatuje duże liczby (np. 1,500,000 -> 1.5M).

    Args:
        value: Liczba do sformatowania

    Returns:
        str: Sformatowana liczba

    Example:
        >>> format_large_number(1500000)
        '1.5M'
        >>> format_large_number(2300000000)
        '2.3B'
    """
    if value is None:
        return 'N/A'

    abs_value = abs(value)

    if abs_value >= 1_000_000_000_000:  # Trillion
        return f"{value / 1_000_000_000_000:.1f}T"
    elif abs_value >= 1_000_000_000:    # Billion
        return f"{value / 1_000_000_000:.1f}B"
    elif abs_value >= 1_000_000:        # Million
        return f"{value / 1_000_000:.1f}M"
    elif abs_value >= 1_000:            # Thousand
        return f"{value / 1_000:.1f}K"
    else:
        return f"{value:.2f}"


def format_percentage(value: float) -> str:
    """
    Formatuje wartość jako procent.

    Args:
        value: Wartość (np. 0.05 dla 5%)

    Returns:
        str: Sformatowany procent

    Example:
        >>> format_percentage(0.0525)
        '+5.25%'
        >>> format_percentage(-0.032)
        '-3.20%'
    """
    if value is None:
        return 'N/A'

    sign = '+' if value > 0 else ''
    return f"{sign}{value * 100:.2f}%"


def get_recommendation_from_score(score: float) -> str:
    """
    Konwertuje score na rekomendację.

    Args:
        score: Score -100 to +100

    Returns:
        str: Recommendation level

    Example:
        >>> get_recommendation_from_score(85)
        'STRONG_BUY'
        >>> get_recommendation_from_score(-50)
        'SELL'
    """
    if score >= SCORE_THRESHOLDS['STRONG_BUY']:
        return 'STRONG_BUY'
    elif score >= SCORE_THRESHOLDS['BUY']:
        return 'BUY'
    elif score >= SCORE_THRESHOLDS['HOLD']:
        return 'HOLD'
    elif score >= SCORE_THRESHOLDS['SELL']:
        return 'SELL'
    else:
        return 'STRONG_SELL'


def get_recommendation_color(recommendation: str) -> str:
    """
    Zwraca kolor dla danej rekomendacji.

    Args:
        recommendation: STRONG_BUY, BUY, HOLD, SELL, STRONG_SELL

    Returns:
        str: Hex color code

    Example:
        >>> get_recommendation_color('STRONG_BUY')
        '#39ff14'
    """
    colors = {
        'STRONG_BUY': '#39ff14',    # Neon green
        'BUY': '#7fff00',           # Chartreuse
        'HOLD': '#ffed4e',          # Neon yellow
        'SELL': '#ff8c00',          # Dark orange
        'STRONG_SELL': '#ff073a',   # Neon red
    }
    return colors.get(recommendation, '#e0e0e0')


# ============================================
# TESTING
# ============================================

if __name__ == "__main__":
    print("STOCKANALYZER - Constants")
    print("=" * 60)

    print("\nTwitter Experts:")
    for expert in TWITTER_EXPERTS:
        print(f"  - {expert}: {EXPERT_DESCRIPTIONS[expert]}")

    print("\nSupported Exchanges:")
    for exchange in SUPPORTED_EXCHANGES:
        suffix = EXCHANGE_SUFFIXES.get(exchange, '')
        print(f"  - {exchange} {f'(suffix: {suffix})' if suffix else ''}")

    print("\nScore Thresholds:")
    for level, threshold in SCORE_THRESHOLDS.items():
        print(f"  - {level}: >= {threshold}")

    print("\nFormatting Tests:")
    print(f"  1,500,000 -> {format_large_number(1500000)}")
    print(f"  2,300,000,000 -> {format_large_number(2300000000)}")
    print(f"  0.0525 -> {format_percentage(0.0525)}")
    print(f"  -0.032 -> {format_percentage(-0.032)}")

    print("\nRecommendation Tests:")
    test_scores = [85, 50, 0, -50, -85]
    for score in test_scores:
        rec = get_recommendation_from_score(score)
        color = get_recommendation_color(rec)
        print(f"  Score {score:+3d} -> {rec:12s} (color: {color})")

    print("\n" + "=" * 60)
