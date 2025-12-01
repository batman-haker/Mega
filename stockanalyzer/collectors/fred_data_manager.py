"""
STOCKANALYZER - FRED Historical Data Manager

Zarządza historycznymi danymi FRED w bazie danych:
- Inicjalne pobieranie dużej ilości danych (365 dni)
- Inkrementalne aktualizacje (tylko nowe dni)
- Szybki odczyt z DB zamiast API

Korzyści:
- 100x szybsze ładowanie (DB vs API)
- Oszczędność API limits
- Pełna historia dla wykresów

Użycie:
    from collectors.fred_data_manager import FredDataManager

    manager = FredDataManager()

    # Pierwsz run - pobierz 365 dni
    manager.initialize_historical_data(days_back=365)

    # Codziennie - aktualizuj tylko nowe
    manager.update_recent_data(days_back=7)

    # Odczytaj z DB
    sofr_data = manager.get_series_data('SOFR', days_back=90)
"""

import sys
from pathlib import Path
from typing import Dict, Optional, List
from datetime import datetime, timedelta
import pandas as pd

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from database.db import DatabaseSession
from database.models import FredHistoricalData
from utils.config import Config
from utils.liquidity_monitor import LiquidityMonitor


class FredDataManager:
    """
    Zarządza historycznymi danymi FRED w bazie danych.

    Strategia:
    1. Pierwsze uruchomienie: Pobierz 365 dni wszystkich serii
    2. Kolejne uruchomienia: Pobierz tylko ostatnie 7 dni (incremental)
    3. Strona Makro: Czyta z DB (instant!), nie z API

    Example:
        >>> manager = FredDataManager()
        >>>
        >>> # Check if we need initial load
        >>> if not manager.has_historical_data():
        >>>     manager.initialize_historical_data(days_back=365)
        >>>
        >>> # Daily update (cron job)
        >>> manager.update_recent_data(days_back=7)
        >>>
        >>> # Get data for analysis
        >>> sofr = manager.get_series_data('SOFR', days_back=90)
    """

    def __init__(self):
        """Initialize manager with FRED API key"""
        self.api_key = Config.FRED_API_KEY
        self.monitor = LiquidityMonitor(fred_api_key=self.api_key)

        # Lista wszystkich serii do pobrania (z liquidity_monitor.py)
        self.series_ids = list(self.monitor.series.values())

    def has_historical_data(self, min_count: int = 100) -> bool:
        """
        Sprawdza czy mamy dane historyczne w bazie.

        Args:
            min_count: Minimum ile punktów danych (default: 100 = ~5 miesięcy)

        Returns:
            bool: True jeśli mamy dane

        Example:
            >>> if not manager.has_historical_data():
            >>>     print("Need to initialize!")
        """
        with DatabaseSession() as session:
            # Sprawdź total count dla kluczowego wskaźnika (SOFR)
            # 247 punktów = ~1 rok danych (bo business days only)
            count = session.query(FredHistoricalData).filter(
                FredHistoricalData.series_id == 'SOFR'
            ).count()

            return count >= min_count

    def get_latest_date(self, series_id: str) -> Optional[datetime]:
        """
        Pobiera datę najnowszego wpisu dla danej serii.

        Args:
            series_id: ID serii (np. 'SOFR', 'VIX')

        Returns:
            datetime lub None jeśli brak danych
        """
        with DatabaseSession() as session:
            latest = session.query(FredHistoricalData).filter(
                FredHistoricalData.series_id == series_id
            ).order_by(FredHistoricalData.date.desc()).first()

            return latest.date if latest else None

    def initialize_historical_data(self, days_back: int = 365, force: bool = False):
        """
        Inicjalne pobieranie dużej ilości danych historycznych.

        UWAGA: To może zająć 2-3 minuty przy pierwszym uruchomieniu!

        Args:
            days_back: Ile dni wstecz pobrać (default: 365)
            force: Czy wymusić pobieranie nawet jeśli dane już są

        Example:
            >>> manager = FredDataManager()
            >>> manager.initialize_historical_data(days_back=365)
            >>> # Poczekaj ~2 min...
            >>> print("Done! Data in database.")
        """
        if not force and self.has_historical_data(min_count=100):
            print(f"[INFO] Historical data already exists. Use force=True to reload.")
            return

        print(f"[INFO] Initializing historical data ({days_back} days)...")
        print(f"   This will take ~2-3 minutes. Please wait...")

        total_series = len(self.series_ids)
        for idx, series_id in enumerate(self.series_ids, 1):
            print(f"   [{idx}/{total_series}] Fetching {series_id}...")

            # Pobierz dane z FRED API
            data = self.monitor.fetch_fred_data(series_id, days_back=days_back)

            if data.empty:
                print(f"       [SKIP] No data for {series_id}")
                continue

            # Zapisz do bazy
            self._save_series_data(series_id, data)
            print(f"       [OK] Saved {len(data)} data points")

        print(f"[OK] Historical data initialized!")
        print(f"   {total_series} series, {days_back} days")

    def update_recent_data(self, days_back: int = 7):
        """
        Inkrementalna aktualizacja - pobiera tylko ostatnie dni.

        To jest SZYBKIE - używaj codziennie!

        Args:
            days_back: Ile dni wstecz zaktualizować (default: 7)

        Example:
            >>> # Cron job - raz dziennie
            >>> manager = FredDataManager()
            >>> manager.update_recent_data(days_back=7)
        """
        print(f"[INFO] Updating recent data (last {days_back} days)...")

        total_series = len(self.series_ids)
        updated_count = 0

        for idx, series_id in enumerate(self.series_ids, 1):
            # Pobierz tylko ostatnie dni
            data = self.monitor.fetch_fred_data(series_id, days_back=days_back)

            if data.empty:
                continue

            # Zapisz/zaktualizuj w bazie
            new_points = self._save_series_data(series_id, data)
            if new_points > 0:
                updated_count += 1
                print(f"   [{idx}/{total_series}] {series_id}: +{new_points} new points")

        print(f"[OK] Updated {updated_count}/{total_series} series")

    def get_series_data(self, series_id: str, days_back: int = 90) -> pd.DataFrame:
        """
        Pobiera dane serii z bazy danych.

        To jest INSTANT - żadnych API calls!

        Args:
            series_id: ID serii (np. 'SOFR', 'VIX')
            days_back: Ile dni wstecz (default: 90)

        Returns:
            DataFrame z kolumnami: date, value

        Example:
            >>> manager = FredDataManager()
            >>> sofr = manager.get_series_data('SOFR', days_back=90)
            >>> print(f"Latest SOFR: {sofr.iloc[-1]['value']}")
        """
        with DatabaseSession() as session:
            start_date = datetime.now() - timedelta(days=days_back)

            records = session.query(FredHistoricalData).filter(
                FredHistoricalData.series_id == series_id,
                FredHistoricalData.date >= start_date
            ).order_by(FredHistoricalData.date).all()

            if not records:
                # Brak danych w DB - zwróć pusty DataFrame
                return pd.DataFrame(columns=['date', 'value'])

            # Convert to DataFrame
            df = pd.DataFrame([
                {'date': r.date, 'value': r.value}
                for r in records
            ])

            return df

    def get_all_series_data(self, days_back: int = 90) -> Dict[str, pd.DataFrame]:
        """
        Pobiera dane wszystkich serii z bazy.

        Args:
            days_back: Ile dni wstecz

        Returns:
            Dict {series_id: DataFrame}

        Example:
            >>> manager = FredDataManager()
            >>> all_data = manager.get_all_series_data(days_back=90)
            >>> sofr = all_data['SOFR']
            >>> vix = all_data['VIX']
        """
        result = {}

        for series_name, series_id in self.monitor.series.items():
            data = self.get_series_data(series_id, days_back=days_back)
            if not data.empty:
                result[series_name] = data

        return result

    def _save_series_data(self, series_id: str, data: pd.DataFrame) -> int:
        """
        Zapisuje dane serii do bazy (INSERT or UPDATE).

        Args:
            series_id: ID serii
            data: DataFrame z kolumnami: date, value

        Returns:
            int: Liczba nowych/zaktualizowanych wpisów
        """
        if data.empty:
            return 0

        new_count = 0

        with DatabaseSession() as session:
            for _, row in data.iterrows():
                # Sprawdź czy wpis już istnieje
                existing = session.query(FredHistoricalData).filter(
                    FredHistoricalData.series_id == series_id,
                    FredHistoricalData.date == row['date']
                ).first()

                if existing:
                    # Update istniejącego wpisu
                    existing.value = float(row['value'])
                    existing.last_updated = datetime.utcnow()
                else:
                    # Insert nowego wpisu
                    new_point = FredHistoricalData(
                        series_id=series_id,
                        date=row['date'],
                        value=float(row['value'])
                    )
                    session.add(new_point)
                    new_count += 1

            session.commit()

        return new_count

    def get_database_stats(self) -> Dict[str, int]:
        """
        Statystyki bazy danych FRED.

        Returns:
            Dict z liczbą wpisów dla każdej serii

        Example:
            >>> stats = manager.get_database_stats()
            >>> print(f"SOFR: {stats['SOFR']} data points")
        """
        stats = {}

        with DatabaseSession() as session:
            for series_name, series_id in self.monitor.series.items():
                count = session.query(FredHistoricalData).filter(
                    FredHistoricalData.series_id == series_id
                ).count()
                stats[series_name] = count

        return stats


# ============================================
# CLI UTILITIES
# ============================================

def main():
    """CLI interface for FRED data management"""
    import argparse

    parser = argparse.ArgumentParser(description='FRED Historical Data Manager')
    parser.add_argument('action', choices=['init', 'update', 'stats', 'check'],
                       help='Action to perform')
    parser.add_argument('--days', type=int, default=365,
                       help='Days to fetch (default: 365 for init, 7 for update)')
    parser.add_argument('--force', action='store_true',
                       help='Force reload even if data exists')

    args = parser.parse_args()

    manager = FredDataManager()

    if args.action == 'init':
        manager.initialize_historical_data(days_back=args.days, force=args.force)

    elif args.action == 'update':
        days = args.days if args.days != 365 else 7  # Default 7 for update
        manager.update_recent_data(days_back=days)

    elif args.action == 'stats':
        stats = manager.get_database_stats()
        print("\n=== FRED Database Statistics ===")
        for series, count in stats.items():
            print(f"  {series:20s}: {count:5d} data points")
        print("=" * 40)

    elif args.action == 'check':
        has_data = manager.has_historical_data()
        print(f"Has historical data: {has_data}")

        if has_data:
            print("\nLatest dates:")
            for series_name in ['sofr', 'vix', 'yield_curve']:
                if series_name in manager.monitor.series:
                    series_id = manager.monitor.series[series_name]
                    latest = manager.get_latest_date(series_id)
                    print(f"  {series_name}: {latest}")


if __name__ == "__main__":
    main()
