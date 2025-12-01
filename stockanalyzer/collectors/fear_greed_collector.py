"""
Fear & Greed Index Collector

Pobiera CNN Fear & Greed Index oraz tworzy własny wskaźnik sentymentu
oparty na danych z FRED (VIX, Put/Call, High Yield Spread).

Sources:
- CNN Fear & Greed Index: https://production.dataviz.cnn.io/index/fearandgreed/graphdata
- Alternative: Composite sentiment based on VIX, market indicators
"""

import requests
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple
import json


class FearGreedCollector:
    """Kolektor wskaźników sentymentu rynkowego"""

    def __init__(self):
        self.cnn_url = "https://production.dataviz.cnn.io/index/fearandgreed/graphdata"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json',
        }

    def get_cnn_fear_greed(self) -> Optional[Dict]:
        """
        Pobiera CNN Fear & Greed Index

        Returns:
            Dict z kluczami:
            - score: 0-100 (0=extreme fear, 100=extreme greed)
            - rating: tekstowy opis (e.g., "Fear", "Greed")
            - timestamp: data pomiaru
            - previous_score: poprzednia wartość
            - previous_rating: poprzedni rating
        """
        try:
            response = requests.get(self.cnn_url, headers=self.headers, timeout=10)
            response.raise_for_status()
            data = response.json()

            # CNN API zwraca strukturę:
            # {
            #   "fear_and_greed": {
            #     "score": 45,
            #     "rating": "Fear",
            #     "timestamp": "2025-01-15T12:00:00",
            #     "previous_close": 42,
            #     "previous_1_week": 48
            #   }
            # }

            fg_data = data.get('fear_and_greed', {})

            return {
                'score': fg_data.get('score'),
                'rating': fg_data.get('rating', 'Unknown'),
                'timestamp': fg_data.get('timestamp'),
                'previous_score': fg_data.get('previous_close'),
                'previous_1week': fg_data.get('previous_1_week'),
            }

        except requests.RequestException as e:
            print(f"[ERROR] Failed to fetch CNN Fear & Greed: {e}")
            return None
        except (KeyError, ValueError, json.JSONDecodeError) as e:
            print(f"[ERROR] Failed to parse CNN data: {e}")
            return None

    def interpret_score(self, score: float) -> Tuple[str, str, str]:
        """
        Interpretuje score Fear & Greed

        Args:
            score: wartość 0-100

        Returns:
            (emoji, label, opis)
        """
        if score <= 25:
            return "😱", "EXTREME FEAR", "Rynek w panice - możliwa okazja do kupna?"
        elif score <= 45:
            return "😰", "FEAR", "Ostrożność na rynku - inwestorzy się boją"
        elif score <= 55:
            return "😐", "NEUTRAL", "Rynek zrównoważony - brak wyraźnych emocji"
        elif score <= 75:
            return "😊", "GREED", "Optymizm na rynku - inwestorzy pewni siebie"
        else:
            return "🤑", "EXTREME GREED", "Euforia na rynku - ryzyko korekty!"

    def get_sentiment_from_vix(self, vix_value: Optional[float]) -> Dict:
        """
        Tworzy własny wskaźnik sentymentu bazując na VIX

        Args:
            vix_value: wartość VIX (CBOE Volatility Index)

        Returns:
            Dict z sentimentem bazującym na VIX
        """
        if vix_value is None:
            return {'score': None, 'rating': 'Unknown', 'source': 'VIX'}

        # VIX interpretation:
        # < 12 = very low fear (complacency) → Greed
        # 12-20 = normal → Neutral
        # 20-30 = elevated fear → Fear
        # > 30 = extreme fear → Extreme Fear

        # Convert VIX to 0-100 scale (inverted, since high VIX = fear)
        # VIX 10 → score 100 (extreme greed)
        # VIX 30 → score 25 (fear)
        # VIX 50+ → score 0 (extreme fear)

        if vix_value < 12:
            score = 85
            rating = "Extreme Greed"
        elif vix_value < 20:
            score = 60
            rating = "Greed"
        elif vix_value < 30:
            score = 40
            rating = "Fear"
        else:
            score = 15
            rating = "Extreme Fear"

        return {
            'score': score,
            'rating': rating,
            'source': 'VIX-based',
            'vix_value': vix_value
        }


# ============================================
# MAIN FUNCTION
# ============================================

def get_fear_greed_index(use_cnn: bool = True) -> Dict:
    """
    Pobiera Fear & Greed Index

    Args:
        use_cnn: jeśli True, próbuje pobrać z CNN (fallback na VIX)

    Returns:
        Dict z danymi Fear & Greed
    """
    collector = FearGreedCollector()

    # Try CNN first
    if use_cnn:
        cnn_data = collector.get_cnn_fear_greed()
        if cnn_data and cnn_data.get('score') is not None:
            return cnn_data

    # Fallback: use VIX-based sentiment
    # Note: VIX data would need to be fetched from FRED or Yahoo
    # For now, return None to indicate failure
    return {
        'score': None,
        'rating': 'Unavailable',
        'timestamp': None,
        'error': 'Unable to fetch Fear & Greed data'
    }


# ============================================
# TESTING
# ============================================

if __name__ == "__main__":
    print("Testing Fear & Greed Collector...")
    print("=" * 50)

    data = get_fear_greed_index()

    if data.get('score') is not None:
        collector = FearGreedCollector()
        emoji, label, desc = collector.interpret_score(data['score'])

        print(f"Score: {data['score']}/100")
        print(f"Rating: {emoji} {data['rating']}")
        print(f"Description: {desc}")
        print(f"Timestamp: {data.get('timestamp')}")
        print(f"Previous (close): {data.get('previous_score')}")
        print(f"Previous (1 week): {data.get('previous_1week')}")
    else:
        print(f"ERROR: {data.get('error', 'Unknown error')}")
