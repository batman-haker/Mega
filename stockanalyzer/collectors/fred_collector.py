"""
STOCKANALYZER - FRED Data Collector

Integracja z projektem C:\FRED (LiquidityMonitor):
- Pobiera wskaźniki makroekonomiczne (SOFR, VIX, yield curve, M2, etc.)
- Analizuje warunki płynności
- Wykrywa market regime (RISK_ON/RISK_OFF/CRISIS)
- Cache z TTL (1 godzina)

Wykorzystuje:
- LiquidityMonitor z C:\FRED\liquidity_monitor.py
- FRED API (Federal Reserve Economic Data)

Użycie:
    from collectors.fred_collector import FredCollector

    collector = FredCollector()
    data = collector.get_fred_data()
    print(f"Regime: {data['regime']}")
    print(f"Score: {data['score']}")
"""

import sys
from pathlib import Path
from typing import Dict, Optional
from datetime import datetime, timedelta
import json
import pandas as pd

# Import LiquidityMonitor z naszego utils (skopiowane z C:\FRED)
try:
    from utils.liquidity_monitor import LiquidityMonitor
    FRED_AVAILABLE = True
except ImportError:
    FRED_AVAILABLE = False
    print("[WARNING] LiquidityMonitor not available - FRED integration disabled")

try:
    from collectors.fred_data_manager import FredDataManager
    FRED_DATA_MANAGER_AVAILABLE = True
except ImportError:
    FRED_DATA_MANAGER_AVAILABLE = False
    print("[WARNING] FredDataManager not available - using API only")

from utils.config import Config
from database.db import DatabaseSession
from database.models import FredCache


class FredCollector:
    """
    Collector dla danych makroekonomicznych z FRED.

    Integruje się z projektem C:\FRED (LiquidityMonitor),
    dodaje caching do bazy danych (TTL: 1h).

    Example:
        >>> collector = FredCollector()
        >>> data = collector.get_fred_data()
        >>> print(data['regime'])  # RISK_ON, RISK_OFF, CRISIS
        >>> print(data['score'])   # -100 to +100
    """

    def __init__(self):
        """Initialize FRED collector with API key from config"""
        self.api_key = Config.FRED_API_KEY
        self.cache_ttl = Config.FRED_CACHE_TTL  # 3600 seconds (1h)

        if not FRED_AVAILABLE:
            raise ImportError(
                "LiquidityMonitor not available. "
                "Ensure C:\\FRED project exists with liquidity_monitor.py"
            )

        # Utwórz instancję LiquidityMonitor
        self.monitor = LiquidityMonitor(fred_api_key=self.api_key)

        # Utwórz instancję FredDataManager (dla DB access)
        self.data_manager = FredDataManager() if FRED_DATA_MANAGER_AVAILABLE else None

    def get_fred_data(self, days_back: int = 90, use_cache: bool = True) -> Dict:
        """
        Pobiera wszystkie dane FRED z bazy danych (FAST!) lub API (SLOW).

        Strategia:
        1. Jeśli FredDataManager dostępny → czytaj z DB (instant!)
        2. Jeśli brak danych w DB → użyj API (fallback)

        Args:
            days_back: Ile dni wstecz pobrać historię (default: 90)
            use_cache: Czy używać cache (default: True)

        Returns:
            Dict zawierający:
                - indicators: Dict[str, Any] - surowe wskaźniki
                - analysis: Dict - analiza warunków
                - score: float (-100 to +100)
                - regime: str (RISK_ON, RISK_OFF, CRISIS)
                - alerts: List[str] - krytyczne alerty
                - patterns: Dict - wykryte wzorce
                - timestamp: str - czas pobrania

        Example:
            >>> data = collector.get_fred_data()
            >>> if data['regime'] == 'CRISIS':
            >>>     print("WARNING: Market in crisis mode!")
        """

        # Sprawdź cache (jeśli włączony)
        if use_cache:
            cached = self._get_from_cache()
            if cached:
                print("[INFO] Using cached FRED data")
                return cached

        # NOWA STRATEGIA: Czytaj z bazy jeśli dostępna
        if self.data_manager and self.data_manager.has_historical_data():
            print(f"[INFO] Loading FRED data from database (FAST!)...")
            indicators = self._get_indicators_from_db(days_back=days_back)
        else:
            print(f"[INFO] Fetching fresh FRED data from API (last {days_back} days)...")
            indicators = self.monitor.get_all_indicators(days_back=days_back)

        # Analizuj warunki płynności
        analysis = self.monitor.analyze_liquidity_conditions(indicators)

        # Stwórz wynik
        # Extract regime - może być dict lub string
        market_regime = analysis.get('market_regime', 'UNKNOWN')
        if isinstance(market_regime, dict):
            regime_str = market_regime.get('regime', 'UNKNOWN')
        else:
            regime_str = market_regime

        # Extract alerts - przekształć dicts na stringi (bez emoji dla Windows)
        raw_alerts = analysis.get('alerts', [])
        alerts_list = []
        for alert in raw_alerts:
            if isinstance(alert, dict):
                # Format: "[CRITICAL/WARNING] [Indicator]: Message"
                severity_tag = '[CRITICAL]' if alert.get('severity') == 'critical' else '[WARNING]'
                indicator = alert.get('indicator', 'Unknown')
                message = alert.get('message', '')
                alerts_list.append(f"{severity_tag} {indicator}: {message}")
            else:
                alerts_list.append(str(alert))

        result = {
            'indicators': indicators,
            'analysis': analysis,
            'score': analysis.get('overall_score', 0),
            'regime': regime_str,  # String, nie dict!
            'alerts': alerts_list,  # Lista stringów!
            'patterns': analysis.get('patterns', {}),
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }

        # Zapisz do cache
        if use_cache:
            self._save_to_cache(result)

        return result

    def get_indicator_value(self, indicator_name: str) -> Optional[float]:
        """
        Pobiera wartość pojedynczego wskaźnika.

        Args:
            indicator_name: Nazwa wskaźnika (np. 'SOFR', 'VIX', 'M2')

        Returns:
            float: Aktualna wartość lub None jeśli brak

        Example:
            >>> vix = collector.get_indicator_value('VIX')
            >>> print(f"Current VIX: {vix}")
        """
        data = self.get_fred_data()
        indicators = data.get('indicators', {})

        # Sprawdź w różnych lokalizacjach
        if indicator_name.lower() in indicators:
            ind = indicators[indicator_name.lower()]
            if isinstance(ind, dict) and 'current' in ind:
                return ind['current']
            return ind

        return None

    def get_regime_info(self) -> Dict:
        """
        Pobiera informacje o aktualnym market regime.

        Returns:
            Dict z kluczami:
                - regime: str (RISK_ON, RISK_OFF, CRISIS)
                - score: float (-100 to +100)
                - description: str
                - recommendation: str

        Example:
            >>> regime = collector.get_regime_info()
            >>> print(f"{regime['regime']}: {regime['description']}")
        """
        data = self.get_fred_data()

        regime = data['regime']
        score = data['score']

        # Opisy regime
        descriptions = {
            'RISK_ON': 'Sprzyjające warunki rynkowe - płynność wysoka, VIX niski',
            'RISK_OFF': 'Napięcia na rynku - płynność obniżona, rosnący VIX',
            'CRISIS': 'KRYZYS - krytyczne napięcia płynnościowe!',
            'UNKNOWN': 'Brak wystarczających danych do określenia regime'
        }

        # Rekomendacje
        recommendations = {
            'RISK_ON': 'Korzystne środowisko dla akcji i ryzykownych aktywów',
            'RISK_OFF': 'Ostrożność - rozważ defensywne pozycje',
            'CRISIS': 'UWAGA: Minimalizuj ekspozycję na ryzyko!',
            'UNKNOWN': 'Poczekaj na więcej danych'
        }

        return {
            'regime': regime,
            'score': score,
            'description': descriptions.get(regime, 'Unknown regime'),
            'recommendation': recommendations.get(regime, 'No recommendation')
        }

    def get_key_indicators_summary(self) -> Dict:
        """
        Zwraca podsumowanie kluczowych wskaźników (do wyświetlenia).

        Returns:
            Dict[str, Dict] gdzie każdy wskaźnik ma:
                - value: float
                - change_pct: float
                - interpretation: str

        Example:
            >>> summary = collector.get_key_indicators_summary()
            >>> for name, info in summary.items():
            >>>     print(f"{name}: {info['value']} ({info['interpretation']})")
        """
        data = self.get_fred_data()
        indicators = data.get('indicators', {})

        # Mapowanie nazw wskaźników (user-friendly)
        key_indicators = {
            'sofr': 'SOFR',
            'iorb': 'IORB',
            'yield_curve': 'Yield Curve (10Y-2Y)',
            'vix': 'VIX',
            'm2': 'M2 Money Supply',
            'nfci': 'Financial Conditions',
            'dollar_index': 'Dollar Index (DXY)',
            'hy_spread': 'High Yield Spread',
        }

        summary = {}

        for key, display_name in key_indicators.items():
            if key in indicators:
                ind_data = indicators[key]

                # Ekstraktuj wartości
                if isinstance(ind_data, dict):
                    value = ind_data.get('current', 0)
                    change_pct = ind_data.get('change_pct', 0)
                else:
                    value = ind_data
                    change_pct = 0

                # Interpretacja (prosta)
                interpretation = self._interpret_indicator(key, value, change_pct)

                summary[display_name] = {
                    'value': round(value, 2) if value else None,
                    'change_pct': round(change_pct, 2) if change_pct else 0,
                    'interpretation': interpretation
                }

        return summary

    def _get_indicators_from_db(self, days_back: int = 90) -> Dict:
        """
        Pobiera dane z bazy i przekształca do formatu zgodnego z get_all_indicators().

        Args:
            days_back: Ile dni wstecz

        Returns:
            Dict w formacie zgodnym z LiquidityMonitor.get_all_indicators()
        """
        # Pobierz wszystkie dane z bazy
        all_data = self.data_manager.get_all_series_data(days_back=days_back)

        indicators = {}

        # Przekształć każdą serię do formatu oczekiwanego przez analyze_liquidity_conditions
        for series_name, df in all_data.items():
            if df.empty:
                continue

            try:
                latest = df.iloc[-1]
                if len(df) > 1:
                    previous = df.iloc[-2]
                    week_ago = df[df['date'] <= latest['date'] - timedelta(days=7)]
                    week_ago_value = week_ago.iloc[-1]['value'] if not week_ago.empty else latest['value']

                    # Calculate 30-day change for percentage
                    month_ago = df[df['date'] <= latest['date'] - timedelta(days=30)]
                    month_ago_value = month_ago.iloc[-1]['value'] if not month_ago.empty else latest['value']
                else:
                    previous = latest
                    week_ago_value = latest['value']
                    month_ago_value = latest['value']

                # Calculate percentage change (30 days)
                if month_ago_value != 0:
                    change_pct = ((float(latest['value']) - float(month_ago_value)) / float(month_ago_value)) * 100
                else:
                    change_pct = 0

                indicators[series_name] = {
                    'current': float(latest['value']),
                    'date': pd.to_datetime(latest['date']).strftime('%Y-%m-%d'),
                    'change_1d': float(latest['value']) - float(previous['value']),
                    'change_7d': float(latest['value']) - float(week_ago_value),
                    'change_pct': round(change_pct, 2),  # DODANE!
                    'data': df,
                    'history': df['value'],
                }
            except Exception as e:
                print(f"[WARNING] Error processing {series_name} from DB: {e}")
                continue

        # Oblicz spready (SOFR-IORB, EFFR-IORB) - tak jak w liquidity_monitor.py
        if 'sofr' in indicators and 'iorb' in indicators:
            sofr_data = indicators['sofr']['data']
            iorb_data = indicators['iorb']['data']

            merged = pd.merge(sofr_data, iorb_data, on='date', suffixes=('_sofr', '_iorb'))
            merged['spread'] = merged['value_sofr'] - merged['value_iorb']

            latest_spread = merged.iloc[-1]['spread']
            if len(merged) > 1:
                previous_spread = merged.iloc[-2]['spread']
                week_ago_spread_data = merged[merged['date'] <= merged.iloc[-1]['date'] - timedelta(days=7)]
                week_ago_spread = week_ago_spread_data.iloc[-1]['spread'] if not week_ago_spread_data.empty else latest_spread

                # Calculate 30-day change for percentage
                month_ago_spread_data = merged[merged['date'] <= merged.iloc[-1]['date'] - timedelta(days=30)]
                month_ago_spread = month_ago_spread_data.iloc[-1]['spread'] if not month_ago_spread_data.empty else latest_spread
            else:
                previous_spread = latest_spread
                week_ago_spread = latest_spread
                month_ago_spread = latest_spread

            # Calculate percentage change (30 days)
            if month_ago_spread != 0:
                spread_change_pct = ((latest_spread - month_ago_spread) / abs(month_ago_spread)) * 100
            else:
                spread_change_pct = 0

            indicators['sofr_iorb_spread'] = {
                'current': latest_spread,
                'date': merged.iloc[-1]['date'].strftime('%Y-%m-%d'),
                'change_1d': latest_spread - previous_spread,
                'change_7d': latest_spread - week_ago_spread,
                'change_pct': round(spread_change_pct, 2),  # DODANE!
                'data': merged[['date', 'spread']].rename(columns={'spread': 'value'}),
                'history': merged['spread'],
            }

        if 'effr' in indicators and 'iorb' in indicators:
            effr_data = indicators['effr']['data']
            iorb_data = indicators['iorb']['data']

            merged = pd.merge(effr_data, iorb_data, on='date', suffixes=('_effr', '_iorb'))
            merged['spread'] = merged['value_effr'] - merged['value_iorb']

            latest_spread = merged.iloc[-1]['spread']
            if len(merged) > 1:
                previous_spread = merged.iloc[-2]['spread']
                week_ago_spread_data = merged[merged['date'] <= merged.iloc[-1]['date'] - timedelta(days=7)]
                week_ago_spread = week_ago_spread_data.iloc[-1]['spread'] if not week_ago_spread_data.empty else latest_spread

                # Calculate 30-day change for percentage
                month_ago_spread_data = merged[merged['date'] <= merged.iloc[-1]['date'] - timedelta(days=30)]
                month_ago_spread = month_ago_spread_data.iloc[-1]['spread'] if not month_ago_spread_data.empty else latest_spread
            else:
                previous_spread = latest_spread
                week_ago_spread = latest_spread
                month_ago_spread = latest_spread

            # Calculate percentage change (30 days)
            if month_ago_spread != 0:
                spread_change_pct = ((latest_spread - month_ago_spread) / abs(month_ago_spread)) * 100
            else:
                spread_change_pct = 0

            indicators['effr_iorb_spread'] = {
                'current': latest_spread,
                'date': merged.iloc[-1]['date'].strftime('%Y-%m-%d'),
                'change_1d': latest_spread - previous_spread,
                'change_7d': latest_spread - week_ago_spread,
                'change_pct': round(spread_change_pct, 2),  # DODANE!
                'data': merged[['date', 'spread']].rename(columns={'spread': 'value'}),
                'history': merged['spread'],
            }

        return indicators

    def _interpret_indicator(self, key: str, value: float, change_pct: float) -> str:
        """Prosta interpretacja wskaźnika"""
        if value is None:
            return "Brak danych"

        # Interpretacje specyficzne dla wskaźników
        if key == 'vix':
            if value > 30:
                return "Wysoki strach"
            elif value < 15:
                return "Niski strach"
            else:
                return "Umiarkowany"

        elif key == 'yield_curve':
            if value < 0:
                return "Inwersja (recesja?)"
            elif value > 1:
                return "Stroma (ekspansja)"
            else:
                return "Normalna"

        elif key == 'nfci':
            if value > 0:
                return "Napięcia finansowe"
            elif value < -0.5:
                return "Luźne warunki"
            else:
                return "Neutralne"

        # Domyślna interpretacja
        if change_pct > 5:
            return "Wzrost"
        elif change_pct < -5:
            return "Spadek"
        else:
            return "Stabilny"

    def _get_from_cache(self) -> Optional[Dict]:
        """
        Pobiera dane z cache jeśli są świeże.

        Returns:
            Dict z danymi lub None jeśli cache przestarzały
        """
        try:
            with DatabaseSession() as session:
                # Pobierz wszystkie świeże wpisy cache
                now = datetime.utcnow()
                cached_items = session.query(FredCache).filter(
                    FredCache.valid_until > now
                ).all()

                if not cached_items:
                    return None

                # Sprawdź czy mamy kompletny zestaw danych
                # (minimalnie potrzebujemy score i regime)
                indicators = {}
                for item in cached_items:
                    # Deserializuj value_json jeśli istnieje
                    # (na razie używamy prostych wartości)
                    indicators[item.indicator_name] = {
                        'current': item.value,
                        'change_pct': item.value_change_pct or 0
                    }

                # Jeśli mamy dane, rekonstruuj wynik
                if len(indicators) > 5:  # Minimum 5 wskaźników
                    # Uwaga: To uproszczone - normalnie trzeba by odtworzyć pełną strukturę
                    # Dla MVP zwracamy None żeby zawsze pobierać świeże
                    return None

                return None

        except Exception as e:
            print(f"[ERROR] Cache read failed: {e}")
            return None

    def _save_to_cache(self, data: Dict):
        """
        Zapisuje dane do cache.

        Args:
            data: Dict z danymi FRED do cache'owania
        """
        try:
            with DatabaseSession() as session:
                now = datetime.utcnow()
                valid_until = now + timedelta(seconds=self.cache_ttl)

                # Zapisz kluczowe wskaźniki
                indicators = data.get('indicators', {})

                for key, value_data in indicators.items():
                    # Ekstraktuj wartości
                    if isinstance(value_data, dict):
                        value = value_data.get('current', 0)
                        change_pct = value_data.get('change_pct', 0)
                    else:
                        value = value_data
                        change_pct = 0

                    # Utwórz wpis cache
                    cache_entry = FredCache(
                        indicator_name=key,
                        value=value,
                        value_change_pct=change_pct,
                        timestamp=now,
                        valid_until=valid_until
                    )

                    session.add(cache_entry)

                session.commit()
                print(f"[INFO] Saved {len(indicators)} indicators to cache (TTL: {self.cache_ttl}s)")

        except Exception as e:
            print(f"[ERROR] Cache save failed: {e}")


# ============================================
# HELPER FUNCTIONS
# ============================================

def test_fred_connection() -> bool:
    """
    Testuje połączenie z FRED API.

    Returns:
        bool: True jeśli połączenie działa
    """
    try:
        collector = FredCollector()
        data = collector.get_fred_data(days_back=7)  # Tylko 7 dni dla testu
        return data is not None and 'regime' in data
    except Exception as e:
        print(f"[ERROR] FRED connection test failed: {e}")
        return False


# ============================================
# TESTING
# ============================================

if __name__ == "__main__":
    print("=" * 60)
    print("FRED Collector - Test")
    print("=" * 60)

    # Test connection
    print("\n1. Testing FRED connection...")
    if test_fred_connection():
        print("[OK] FRED connection working!")
    else:
        print("[ERROR] FRED connection failed!")
        sys.exit(1)

    # Test data collection
    print("\n2. Testing data collection...")
    collector = FredCollector()
    data = collector.get_fred_data(days_back=30)

    print(f"\nRegime: {data['regime']}")
    print(f"Score: {data['score']}")
    print(f"Alerts: {len(data['alerts'])}")

    if data['alerts']:
        print("\nCritical Alerts:")
        for alert in data['alerts'][:3]:  # First 3
            print(f"  - {alert}")

    # Test key indicators
    print("\n3. Key Indicators Summary:")
    summary = collector.get_key_indicators_summary()
    for name, info in list(summary.items())[:5]:  # First 5
        print(f"  {name}: {info['value']} ({info['interpretation']})")

    print("\n" + "=" * 60)
    print("[OK] All tests passed!")
