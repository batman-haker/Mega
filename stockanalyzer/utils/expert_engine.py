"""
EXPERT ENGINE - AI Investment Council System

System do ładowania profili ekspertów i generowania ich opinii
o spółkach przy użyciu Google Gemini AI.

Architektura:
1. Offline: Przygotowane profile JSON ekspertów (kompresja wiedzy)
2. Online: Profile + dane rynkowe -> Gemini Flash -> opinia eksperta

Usage:
    from utils.expert_engine import load_profiles, get_expert_opinion

    profiles = load_profiles()
    market_data = get_market_data('AAPL')
    macro_data = get_macro_data()

    opinion = get_expert_opinion(profiles[0], 'AAPL', market_data, macro_data)
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import yfinance as yf
import pandas as pd
import numpy as np
import google.generativeai as genai
from utils.config import Config


# ============================================
# CONFIGURATION
# ============================================

# Inicjalizacja Gemini API
genai.configure(api_key=Config.GOOGLE_API_KEY)

# Profile directory
PROFILES_DIR = Config.BASE_DIR / 'data' / 'profiles'


# ============================================
# PROFILE LOADING
# ============================================

def load_profiles() -> List[Dict]:
    """
    Ładuje wszystkie profile ekspertów z data/profiles/*.json

    Returns:
        Lista słowników z profilami ekspertów

    Example:
        >>> profiles = load_profiles()
        >>> print(f"Loaded {len(profiles)} experts")
        >>> print(profiles[0]['name'])
        'Daniel Kostecki (Gra Płynności)'
    """
    profiles = []

    if not PROFILES_DIR.exists():
        print(f"[WARNING] Profiles directory not found: {PROFILES_DIR}")
        return profiles

    for file_path in PROFILES_DIR.glob('*.json'):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                profile = json.load(f)
                profiles.append(profile)
                print(f"[INFO] Loaded profile: {profile.get('name', 'Unknown')}")
        except json.JSONDecodeError as e:
            print(f"[ERROR] Failed to parse {file_path.name}: {e}")
        except Exception as e:
            print(f"[ERROR] Failed to load {file_path.name}: {e}")

    return profiles


# ============================================
# MARKET DATA FETCHERS
# ============================================

def calculate_rsi(prices: pd.Series, period: int = 14) -> float:
    """
    Oblicza RSI (Relative Strength Index)

    Args:
        prices: Seria cen zamknięcia
        period: Okres RSI (default: 14)

    Returns:
        Wartość RSI (0-100)
    """
    if len(prices) < period + 1:
        return None

    delta = prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()

    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))

    return rsi.iloc[-1] if not pd.isna(rsi.iloc[-1]) else None


def get_market_data(ticker: str, period: str = '3mo') -> Dict:
    """
    Pobiera dane rynkowe o spółce z Yahoo Finance

    Args:
        ticker: Symbol tickera (np. 'AAPL', 'NVDA')
        period: Okres historyczny ('3mo', '6mo', '1y')

    Returns:
        Dict z danymi:
        - ticker: str
        - current_price: float
        - change_percent: float
        - pe_ratio: float
        - market_cap: float
        - rsi_14: float
        - trend: str ('Wzrostowy', 'Spadkowy', 'Boczny')
        - volume_avg: float
        - high_52w: float
        - low_52w: float

    Example:
        >>> data = get_market_data('AAPL')
        >>> print(f"Price: ${data['current_price']:.2f}")
        >>> print(f"RSI: {data['rsi_14']:.1f}")
    """
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        hist = stock.history(period=period)

        if hist.empty:
            raise ValueError(f"No data found for {ticker}")

        # Current price and change
        current_price = hist['Close'].iloc[-1]
        prev_close = hist['Close'].iloc[-2] if len(hist) > 1 else current_price
        change_percent = ((current_price - prev_close) / prev_close) * 100

        # RSI
        rsi = calculate_rsi(hist['Close'])

        # Trend analysis (simple: 50-day MA)
        if len(hist) >= 50:
            ma_50 = hist['Close'].rolling(50).mean().iloc[-1]
            if current_price > ma_50 * 1.02:
                trend = "Wzrostowy"
            elif current_price < ma_50 * 0.98:
                trend = "Spadkowy"
            else:
                trend = "Boczny"
        else:
            trend = "Brak danych"

        # 52-week high/low
        high_52w = hist['High'].max()
        low_52w = hist['Low'].min()

        return {
            'ticker': ticker,
            'current_price': round(current_price, 2),
            'change_percent': round(change_percent, 2),
            'pe_ratio': info.get('trailingPE', None),
            'market_cap': info.get('marketCap', None),
            'rsi_14': round(rsi, 1) if rsi else None,
            'trend': trend,
            'volume_avg': int(hist['Volume'].mean()),
            'high_52w': round(high_52w, 2),
            'low_52w': round(low_52w, 2),
            'sector': info.get('sector', 'Unknown'),
            'industry': info.get('industry', 'Unknown'),
        }

    except Exception as e:
        print(f"[ERROR] Failed to fetch market data for {ticker}: {e}")
        return {
            'ticker': ticker,
            'error': str(e),
            'current_price': None,
        }


def get_macro_data() -> Dict:
    """
    Pobiera kluczowe dane makroekonomiczne

    Wykorzystuje dane z liquidity_monitor jeśli dostępne,
    w przeciwnym razie zwraca fallback values.

    Returns:
        Dict z danymi makro:
        - fed_funds_rate: float (Stopa FED)
        - treasury_yield_10y: float (Rentowność 10Y)
        - yield_curve: float (Spread 10Y-2Y)
        - vix: float (Indeks zmienności)
        - liquidity_score: int (Ogólny score płynności)

    Example:
        >>> macro = get_macro_data()
        >>> print(f"FED Rate: {macro['fed_funds_rate']}%")
    """
    try:
        # Spróbuj użyć liquidity_monitor
        from utils.liquidity_monitor import get_liquidity_data

        indicators, score, _ = get_liquidity_data()

        # Wyciągnij kluczowe wskaźniki
        vix_data = indicators.get('vix', {})
        vix_value = vix_data.get('value', None)

        # Yield curve (spread)
        yield_curve_data = indicators.get('t10y2y', {})
        yield_curve = yield_curve_data.get('value', None)

        return {
            'fed_funds_rate': 5.25,  # Fallback - update manually or from FRED
            'treasury_yield_10y': 4.5,  # Fallback
            'yield_curve': yield_curve if yield_curve else 0.55,
            'vix': vix_value if vix_value else 16.4,
            'liquidity_score': score,
            'timestamp': datetime.now().isoformat(),
        }

    except Exception as e:
        print(f"[WARNING] Failed to fetch macro data from liquidity_monitor: {e}")

        # Fallback: Return conservative estimates
        return {
            'fed_funds_rate': 5.25,
            'treasury_yield_10y': 4.5,
            'yield_curve': 0.55,
            'vix': 16.4,
            'liquidity_score': 30,  # Neutral
            'timestamp': datetime.now().isoformat(),
            'note': 'Fallback values - liquidity monitor unavailable'
        }


# ============================================
# AI OPINION GENERATION
# ============================================

def build_expert_prompt(profile: Dict, ticker: str, market_data: Dict, macro_data: Dict) -> str:
    """
    Buduje prompt dla Gemini na podstawie profilu eksperta i danych rynkowych

    Args:
        profile: Profil eksperta (JSON)
        ticker: Symbol spółki
        market_data: Dane rynkowe o spółce
        macro_data: Dane makroekonomiczne

    Returns:
        Sformatowany prompt dla LLM
    """
    # Extract key profile elements
    system_prompt = profile.get('system_prompt', '')
    mental_models = profile.get('mental_models', [])
    decision_logic = profile.get('decision_logic', [])

    # Format mental models
    models_text = "\n".join([
        f"- **{m['concept']}**: {m['logic']}"
        for m in mental_models
    ])

    # Format decision logic
    logic_text = "\n".join([
        f"- Gdy: {d['condition']} → {d['action']} (Powód: {d['reasoning']})"
        for d in decision_logic
    ])

    # Format market data
    market_summary = f"""
DANE O SPÓŁCE {ticker}:
- Cena: ${market_data.get('current_price', 'N/A')}
- Zmiana: {market_data.get('change_percent', 'N/A')}%
- P/E: {market_data.get('pe_ratio', 'N/A')}
- RSI(14): {market_data.get('rsi_14', 'N/A')}
- Trend: {market_data.get('trend', 'N/A')}
- Sektor: {market_data.get('sector', 'N/A')}
- Branża: {market_data.get('industry', 'N/A')}
- 52W High: ${market_data.get('high_52w', 'N/A')}
- 52W Low: ${market_data.get('low_52w', 'N/A')}
"""

    # Format macro data
    macro_summary = f"""
DANE MAKROEKONOMICZNE:
- Stopa FED: {macro_data.get('fed_funds_rate', 'N/A')}%
- Rentowność 10Y: {macro_data.get('treasury_yield_10y', 'N/A')}%
- Krzywa dochodowości (10Y-2Y): {macro_data.get('yield_curve', 'N/A')}%
- VIX: {macro_data.get('vix', 'N/A')}
- Liquidity Score: {macro_data.get('liquidity_score', 'N/A')}
"""

    # Build final prompt
    prompt = f"""
{system_prompt}

TWOJE MODELE MYŚLOWE:
{models_text}

TWOJA LOGIKA DECYZYJNA:
{logic_text}

===== AKTUALNA SYTUACJA RYNKOWA =====

{market_summary}

{macro_summary}

===== ZADANIE =====

Użytkownik pyta Cię o opinię na temat spółki **{ticker}**.

Odpowiedz jako {profile.get('name', 'ekspert')}, używając swojego unikalnego stylu i słownictwa.

Twoja odpowiedź MUSI zawierać:
1. **WERDYKT** (KUPUJ / SPRZEDAJ / CZEKAJ / UNIKAJ)
2. **UZASADNIENIE** (2-3 zdania w Twoim stylu, odwołujące się do Twoich modeli myślowych)
3. **KLUCZOWY WSKAŹNIK** (Na co patrzysz w pierwszej kolejności?)
4. **POZIOM PEWNOŚCI** (Niska / Średnia / Wysoka)

Odpowiedz zwięźle (max 150 słów). Użyj swojego charakterystycznego języka i terminologii.

ODPOWIEDŹ:
"""

    return prompt


def get_expert_opinion(
    profile: Dict,
    ticker: str,
    market_data: Dict,
    macro_data: Dict,
    model_name: str = 'gemini-1.5-flash'
) -> Dict:
    """
    Generuje opinię eksperta o spółce używając Gemini AI

    Args:
        profile: Profil eksperta
        ticker: Symbol spółki
        market_data: Dane rynkowe
        macro_data: Dane makro
        model_name: Model Gemini do użycia (default: gemini-1.5-flash)

    Returns:
        Dict z opinią:
        - expert_name: str
        - expert_id: str
        - ticker: str
        - verdict: str
        - opinion: str (pełna opinia)
        - timestamp: str
        - model_used: str

    Example:
        >>> opinion = get_expert_opinion(profile, 'AMD', market_data, macro_data)
        >>> print(f"{opinion['expert_name']}: {opinion['verdict']}")
        >>> print(opinion['opinion'])
    """
    try:
        # Build prompt
        prompt = build_expert_prompt(profile, ticker, market_data, macro_data)

        # Generate content
        model = genai.GenerativeModel(model_name)
        response = model.generate_content(prompt)

        opinion_text = response.text

        # Extract verdict (simple regex/search)
        verdict = "CZEKAJ"  # Default
        if "KUPUJ" in opinion_text.upper():
            verdict = "KUPUJ"
        elif "SPRZEDAJ" in opinion_text.upper():
            verdict = "SPRZEDAJ"
        elif "UNIKAJ" in opinion_text.upper():
            verdict = "UNIKAJ"

        return {
            'expert_name': profile.get('name', 'Unknown'),
            'expert_id': profile.get('id', 'unknown'),
            'expert_role': profile.get('role', ''),
            'avatar': profile.get('avatar', ''),
            'ticker': ticker,
            'verdict': verdict,
            'opinion': opinion_text,
            'timestamp': datetime.now().isoformat(),
            'model_used': model_name,
        }

    except Exception as e:
        print(f"[ERROR] Failed to generate opinion for {profile.get('name', 'Unknown')}: {e}")
        return {
            'expert_name': profile.get('name', 'Unknown'),
            'expert_id': profile.get('id', 'unknown'),
            'ticker': ticker,
            'verdict': 'ERROR',
            'opinion': f"Nie udało się wygenerować opinii: {str(e)}",
            'timestamp': datetime.now().isoformat(),
            'error': str(e),
        }


# ============================================
# TESTING
# ============================================

if __name__ == "__main__":
    print("=" * 60)
    print("EXPERT ENGINE - Test Run")
    print("=" * 60)

    # Load profiles
    print("\n[1] Loading expert profiles...")
    profiles = load_profiles()
    print(f"    Loaded {len(profiles)} expert(s)")

    # Get market data
    print("\n[2] Fetching market data for AMD...")
    market_data = get_market_data('AMD')
    print(f"    AMD: ${market_data.get('current_price')} ({market_data.get('change_percent')}%)")
    print(f"    RSI: {market_data.get('rsi_14')}")

    # Get macro data
    print("\n[3] Fetching macro data...")
    macro_data = get_macro_data()
    print(f"    VIX: {macro_data.get('vix')}")
    print(f"    Liquidity Score: {macro_data.get('liquidity_score')}")

    # Generate opinion
    if profiles:
        print(f"\n[4] Generating opinion from {profiles[0].get('name')}...")
        opinion = get_expert_opinion(profiles[0], 'AMD', market_data, macro_data)
        print(f"\n    EXPERT: {opinion['expert_name']}")
        print(f"    VERDICT: {opinion['verdict']}")
        print(f"    OPINION:\n{opinion['opinion']}")

    print("\n" + "=" * 60)
    print("Test completed!")
    print("=" * 60)
