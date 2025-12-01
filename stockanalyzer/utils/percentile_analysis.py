"""
STOCKANALYZER - Percentile Analysis

Oblicza percentyle dla wskaźników FRED - pokazuje gdzie obecna wartość
jest względem historii (0-100%).

Przykład:
- VIX = 18.5, percentile = 45% → "Poniżej mediany historycznej"
- SOFR-IORB = 8 bps, percentile = 15% → "Bardzo nisko, płynność dobra"

Użycie:
    from utils.percentile_analysis import calculate_percentile, interpret_percentile

    percentile = calculate_percentile(current_value, historical_values)
    interpretation = interpret_percentile('VIX', percentile)
"""

import numpy as np
import pandas as pd
from typing import List, Tuple, Optional


def calculate_percentile(current_value: float, historical_data: pd.Series) -> float:
    """
    Oblicza percentyl obecnej wartości względem danych historycznych.

    Args:
        current_value: Obecna wartość wskaźnika
        historical_data: Pandas Series z wartościami historycznymi

    Returns:
        float: Percentyl (0-100)

    Example:
        >>> history = pd.Series([10, 15, 20, 25, 30])
        >>> calculate_percentile(22, history)
        60.0  # 22 jest na 60th percentile
    """
    if historical_data.empty or current_value is None:
        return 50.0  # Default to median

    # Usuń NaN
    historical_data = historical_data.dropna()

    if len(historical_data) == 0:
        return 50.0

    # Oblicz percentyl
    percentile = (historical_data < current_value).sum() / len(historical_data) * 100

    return round(percentile, 1)


def interpret_percentile(
    indicator_name: str,
    percentile: float,
    higher_is_good: bool = None
) -> Tuple[str, str, str]:
    """
    Interpretuje percentyl dla danego wskaźnika.

    Args:
        indicator_name: Nazwa wskaźnika (np. 'VIX', 'SOFR')
        percentile: Wartość percentyla (0-100)
        higher_is_good: Czy wyższa wartość jest dobra (opcjonalne, auto-detect)

    Returns:
        Tuple: (status_text, status_emoji, status_color)

    Example:
        >>> text, emoji, color = interpret_percentile('VIX', 85)
        >>> print(f"{emoji} {text}")
        🔴 Bardzo Wysoko (historyczny szczyt)
    """
    # Auto-detect czy higher is good (dla znanych wskaźników)
    if higher_is_good is None:
        higher_is_good = _is_higher_better(indicator_name)

    # Interpretacja bazująca na percentylu
    if percentile >= 95:
        level = "Ekstremalnie Wysoko"
        detail = "99th percentile - rzadka sytuacja!"
    elif percentile >= 85:
        level = "Bardzo Wysoko"
        detail = "Górne 15% historii"
    elif percentile >= 70:
        level = "Wysoko"
        detail = "Powyżej 3. kwartyla"
    elif percentile >= 55:
        level = "Nieco Powyżej Mediany"
        detail = "Powyżej średniej"
    elif percentile >= 45:
        level = "Blisko Mediany"
        detail = "Typowa wartość"
    elif percentile >= 30:
        level = "Nieco Poniżej Mediany"
        detail = "Poniżej średniej"
    elif percentile >= 15:
        level = "Nisko"
        detail = "Poniżej 1. kwartyla"
    elif percentile >= 5:
        level = "Bardzo Nisko"
        detail = "Dolne 15% historii"
    else:
        level = "Ekstremalnie Nisko"
        detail = "1st percentile - rzadka sytuacja!"

    # Określ kolor i emoji
    if higher_is_good:
        # Dla wskaźników gdzie wyżej = lepiej (np. Rezerwy)
        if percentile >= 70:
            emoji = "🟢"
            color = "green"
        elif percentile >= 30:
            emoji = "🟡"
            color = "orange"
        else:
            emoji = "🔴"
            color = "red"
    else:
        # Dla wskaźników gdzie niżej = lepiej (np. VIX, spreads)
        if percentile >= 70:
            emoji = "🔴"
            color = "red"
        elif percentile >= 30:
            emoji = "🟡"
            color = "orange"
        else:
            emoji = "🟢"
            color = "green"

    status_text = f"{level} ({percentile:.0f}th percentile)"
    full_text = f"{status_text} - {detail}"

    return full_text, emoji, color


def _is_higher_better(indicator_name: str) -> bool:
    """
    Określa czy dla danego wskaźnika wyższa wartość jest lepsza.

    Args:
        indicator_name: Nazwa wskaźnika

    Returns:
        bool: True jeśli wyżej = lepiej
    """
    # Wskaźniki gdzie NIŻEJ = LEPIEJ (risk indicators)
    lower_is_better = [
        'vix', 'volatility',
        'spread', 'sofr_iorb_spread', 'effr_iorb_spread',
        'hy_spread', 'high_yield_spread',
        'nfci',  # NFCI > 0 = napięcia
        'tga',  # Wysoki TGA = zabiera płynność
        'reverse_repo', 'rrp',  # Wysoki RRP = kasa zaparkowana
    ]

    # Wskaźniki gdzie WYŻEJ = LEPIEJ (liquidity indicators)
    higher_is_better = [
        'reserves', 'reserve', 'rezerwy',
        'fed_balance', 'balance',
        'm2', 'money_supply',
        'net_liquidity',
    ]

    name_lower = indicator_name.lower()

    # Check if in lower_is_better
    if any(keyword in name_lower for keyword in lower_is_better):
        return False

    # Check if in higher_is_better
    if any(keyword in name_lower for keyword in higher_is_better):
        return True

    # Default: neutral (treat middle as best)
    return None


def get_percentile_color_gradient(percentile: float, reverse: bool = False) -> str:
    """
    Zwraca kolor gradientowy dla percentyla.

    Args:
        percentile: Wartość percentyla (0-100)
        reverse: Odwróć kolory (True dla wskaźników gdzie niżej = lepiej)

    Returns:
        str: RGB color code

    Example:
        >>> color = get_percentile_color_gradient(75, reverse=False)
        >>> # Returns green-ish color
    """
    if reverse:
        # Odwróć skalę
        percentile = 100 - percentile

    # Gradient od czerwonego (0) przez żółty (50) do zielonego (100)
    if percentile < 50:
        # Red to Yellow (0-50)
        ratio = percentile / 50
        r = 255
        g = int(255 * ratio)
        b = 0
    else:
        # Yellow to Green (50-100)
        ratio = (percentile - 50) / 50
        r = int(255 * (1 - ratio))
        g = 255
        b = 0

    return f"rgb({r}, {g}, {b})"


# ============================================
# TESTING
# ============================================

if __name__ == "__main__":
    print("Percentile Analysis - Testing")
    print("=" * 60)

    # Test data
    historical = pd.Series([10, 12, 15, 18, 20, 22, 25, 28, 30])
    current = 24

    percentile = calculate_percentile(current, historical)
    print(f"\nCurrent value: {current}")
    print(f"Historical: {historical.tolist()}")
    print(f"Percentile: {percentile}%")

    # Test interpretation
    print("\n--- VIX Interpretations ---")
    for pct in [5, 25, 50, 75, 95]:
        text, emoji, color = interpret_percentile('VIX', pct)
        print(f"{emoji} {pct}%: {text} (color: {color})")

    print("\n--- Reserves Interpretations ---")
    for pct in [5, 25, 50, 75, 95]:
        text, emoji, color = interpret_percentile('reserves', pct)
        print(f"{emoji} {pct}%: {text} (color: {color})")

    print("\n" + "=" * 60)
