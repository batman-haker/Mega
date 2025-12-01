"""
STOCKANALYZER - Regime History

Oblicza historię market regime (RISK_ON/RISK_OFF/CRISIS) dla każdego dnia.
Tworzy timeline pokazujący jak zmieniał się stan rynku w czasie.

Użycie:
    from utils.regime_history import calculate_regime_history, get_regime_stats

    history_df = calculate_regime_history(indicators_data)
    stats = get_regime_stats(history_df)
"""

import pandas as pd
import numpy as np
from typing import Dict, Tuple
from datetime import datetime, timedelta


def calculate_regime_for_day(
    vix: float,
    sofr_iorb_spread: float,
    reserves: float,
    nfci: float = None
) -> Tuple[str, float]:
    """
    Oblicza market regime dla pojedynczego dnia bazując na wskaźnikach.

    Args:
        vix: Wartość VIX
        sofr_iorb_spread: Spread SOFR-IORB (w bps)
        reserves: Rezerwy bankowe (w miliardach)
        nfci: National Financial Conditions Index (opcjonalnie)

    Returns:
        Tuple: (regime_name, confidence_score)
            - regime_name: 'RISK_ON', 'RISK_OFF', 'CRISIS', 'UNKNOWN'
            - confidence_score: 0-100 (pewność klasyfikacji)

    Example:
        >>> regime, confidence = calculate_regime_for_day(18.5, 8, 3200)
        >>> print(f"{regime} (confidence: {confidence}%)")
        RISK_ON (confidence: 85%)
    """
    # Domyślnie UNKNOWN jeśli brak danych
    if vix is None or sofr_iorb_spread is None:
        return 'UNKNOWN', 0

    # Scoring system (similar to liquidity_monitor.py)
    score = 0
    factors = 0

    # VIX scoring (im niższy, tym lepiej)
    if vix is not None:
        if vix < 15:
            score += 40  # Very calm
        elif vix < 20:
            score += 20  # Calm
        elif vix < 25:
            score += 0   # Neutral
        elif vix < 35:
            score -= 30  # Elevated fear
        else:
            score -= 60  # Extreme fear
        factors += 1

    # SOFR-IORB Spread (im niższy, tym lepiej)
    if sofr_iorb_spread is not None:
        if sofr_iorb_spread < 5:
            score += 30  # Very tight
        elif sofr_iorb_spread < 10:
            score += 15  # Normal
        elif sofr_iorb_spread < 15:
            score += 0   # Slight stress
        elif sofr_iorb_spread < 25:
            score -= 30  # Stress
        else:
            score -= 50  # Severe stress
        factors += 1

    # Reserves (im wyższe, tym lepiej)
    if reserves is not None:
        if reserves > 3500:
            score += 30  # Ample+
        elif reserves > 3000:
            score += 15  # Ample
        elif reserves > 2800:
            score += 0   # Sufficient
        elif reserves > 2500:
            score -= 20  # Scarce
        else:
            score -= 40  # Very scarce
        factors += 1

    # NFCI (National Financial Conditions)
    if nfci is not None:
        if nfci < -0.5:
            score += 20  # Loose conditions
        elif nfci < 0:
            score += 10  # Normal
        elif nfci < 0.5:
            score -= 10  # Tightening
        else:
            score -= 30  # Tight conditions
        factors += 1

    # Normalize score to -100 to +100
    if factors > 0:
        normalized_score = score / factors
    else:
        normalized_score = 0

    # Determine regime based on score
    if normalized_score >= 20:
        regime = 'RISK_ON'
        confidence = min(100, 50 + normalized_score)
    elif normalized_score >= -20:
        regime = 'RISK_OFF'
        confidence = min(100, 50 + abs(normalized_score))
    else:
        regime = 'CRISIS'
        confidence = min(100, 50 + abs(normalized_score))

    return regime, round(confidence, 1)


def calculate_regime_history(indicators: Dict) -> pd.DataFrame:
    """
    Oblicza historię regime dla wszystkich dni gdzie mamy dane.

    Args:
        indicators: Dict z danymi wskaźników (z fred_collector)

    Returns:
        DataFrame z kolumnami: date, regime, confidence, vix, spread, reserves

    Example:
        >>> history = calculate_regime_history(fred_data['indicators'])
        >>> print(history.tail())
              date     regime  confidence    vix  spread  reserves
        2024-11-25  RISK_ON      75.0    17.5     8.2    3200.0
    """
    # Extract data series
    vix_data = indicators.get('vix', {}).get('data')
    spread_data = indicators.get('sofr_iorb_spread', {}).get('data')
    reserves_data = indicators.get('reserves_alt', {}).get('data')
    nfci_data = indicators.get('nfci', {}).get('data')

    if vix_data is None or spread_data is None:
        # Return empty DataFrame if missing critical data
        return pd.DataFrame(columns=['date', 'regime', 'confidence', 'vix', 'spread', 'reserves'])

    # Merge all data on date
    result = vix_data[['date', 'value']].copy()
    result = result.rename(columns={'value': 'vix'})

    if spread_data is not None:
        spread_df = spread_data[['date', 'value']].copy()
        spread_df = spread_df.rename(columns={'value': 'spread'})
        result = result.merge(spread_df, on='date', how='inner')
    else:
        result['spread'] = None

    if reserves_data is not None:
        reserves_df = reserves_data[['date', 'value']].copy()
        reserves_df = reserves_df.rename(columns={'value': 'reserves'})
        result = result.merge(reserves_df, on='date', how='left')
    else:
        result['reserves'] = None

    if nfci_data is not None:
        nfci_df = nfci_data[['date', 'value']].copy()
        nfci_df = nfci_df.rename(columns={'value': 'nfci'})
        result = result.merge(nfci_df, on='date', how='left')
    else:
        result['nfci'] = None

    # Calculate regime for each day
    regimes = []
    confidences = []

    for _, row in result.iterrows():
        regime, confidence = calculate_regime_for_day(
            vix=row.get('vix'),
            sofr_iorb_spread=row.get('spread'),
            reserves=row.get('reserves'),
            nfci=row.get('nfci')
        )
        regimes.append(regime)
        confidences.append(confidence)

    result['regime'] = regimes
    result['confidence'] = confidences

    # Sort by date
    result = result.sort_values('date').reset_index(drop=True)

    return result


def get_regime_stats(history_df: pd.DataFrame) -> Dict:
    """
    Oblicza statystyki regime history.

    Args:
        history_df: DataFrame z historią regime (z calculate_regime_history)

    Returns:
        Dict ze statystykami:
            - regime_counts: Liczba dni w każdym regime
            - regime_percentages: Procent czasu w każdym regime
            - last_regime_change: Data ostatniej zmiany regime
            - current_regime: Obecny regime
            - longest_streak: Najdłuższy ciąg tego samego regime

    Example:
        >>> stats = get_regime_stats(history_df)
        >>> print(f"Current: {stats['current_regime']}")
        >>> print(f"RISK_ON: {stats['regime_percentages']['RISK_ON']:.1f}%")
    """
    if history_df.empty:
        return {
            'regime_counts': {},
            'regime_percentages': {},
            'last_regime_change': None,
            'current_regime': 'UNKNOWN',
            'longest_streak': {'regime': 'UNKNOWN', 'days': 0}
        }

    # Count days in each regime
    regime_counts = history_df['regime'].value_counts().to_dict()

    # Calculate percentages
    total_days = len(history_df)
    regime_percentages = {
        regime: (count / total_days * 100)
        for regime, count in regime_counts.items()
    }

    # Current regime
    current_regime = history_df.iloc[-1]['regime']

    # Find last regime change
    last_regime_change = None
    if len(history_df) > 1:
        for i in range(len(history_df) - 1, 0, -1):
            if history_df.iloc[i]['regime'] != history_df.iloc[i-1]['regime']:
                last_regime_change = history_df.iloc[i]['date']
                break

    # Find longest streak
    longest_streak = {'regime': 'UNKNOWN', 'days': 0, 'start_date': None, 'end_date': None}
    current_streak_regime = None
    current_streak_length = 0
    current_streak_start = None

    for i, row in history_df.iterrows():
        if row['regime'] != current_streak_regime:
            # Streak ended, check if it was longest
            if current_streak_length > longest_streak['days']:
                longest_streak = {
                    'regime': current_streak_regime,
                    'days': current_streak_length,
                    'start_date': current_streak_start,
                    'end_date': history_df.iloc[i-1]['date'] if i > 0 else None
                }
            # Start new streak
            current_streak_regime = row['regime']
            current_streak_length = 1
            current_streak_start = row['date']
        else:
            current_streak_length += 1

    # Check last streak
    if current_streak_length > longest_streak['days']:
        longest_streak = {
            'regime': current_streak_regime,
            'days': current_streak_length,
            'start_date': current_streak_start,
            'end_date': history_df.iloc[-1]['date']
        }

    return {
        'regime_counts': regime_counts,
        'regime_percentages': regime_percentages,
        'last_regime_change': last_regime_change,
        'current_regime': current_regime,
        'longest_streak': longest_streak,
        'total_days': total_days
    }


def detect_regime_transitions(history_df: pd.DataFrame) -> pd.DataFrame:
    """
    Wykrywa wszystkie zmiany regime (transition points).

    Args:
        history_df: DataFrame z historią regime

    Returns:
        DataFrame z transition points (date, from_regime, to_regime)

    Example:
        >>> transitions = detect_regime_transitions(history_df)
        >>> print(transitions)
              date     from_regime  to_regime
        2024-03-15   RISK_ON      RISK_OFF
        2024-05-20   RISK_OFF     RISK_ON
    """
    if history_df.empty or len(history_df) < 2:
        return pd.DataFrame(columns=['date', 'from_regime', 'to_regime'])

    transitions = []

    for i in range(1, len(history_df)):
        current = history_df.iloc[i]
        previous = history_df.iloc[i-1]

        if current['regime'] != previous['regime']:
            transitions.append({
                'date': current['date'],
                'from_regime': previous['regime'],
                'to_regime': current['regime']
            })

    return pd.DataFrame(transitions)


# ============================================
# TESTING
# ============================================

if __name__ == "__main__":
    print("Regime History - Testing")
    print("=" * 60)

    # Test single day calculation
    print("\n1. Testing single day regime calculation:")
    test_cases = [
        (15, 5, 3500, "RISK_ON (low VIX, tight spread, ample reserves)"),
        (25, 18, 2900, "RISK_OFF (elevated VIX, stress spread)"),
        (45, 30, 2400, "CRISIS (high VIX, severe stress, low reserves)"),
    ]

    for vix, spread, reserves, expected in test_cases:
        regime, confidence = calculate_regime_for_day(vix, spread, reserves)
        print(f"  VIX={vix}, Spread={spread}, Reserves={reserves}B")
        print(f"  → {regime} (confidence: {confidence}%)")
        print(f"  Expected: {expected}\n")

    print("=" * 60)
