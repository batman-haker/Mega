"""
STOCKANALYZER - Daily FRED Data Update Script

Codziennie aktualizuje dane FRED w bazie danych.
Tylko pobiera ostatnie 7 dni - szybkie i efektywne!

Usage:
    py update_fred_daily.py

Schedule with Windows Task Scheduler:
    - Run daily at 9:00 AM (after markets open)
    - Trigger: Daily, 9:00 AM
    - Action: py C:\\MEGABOT\\stockanalyzer\\scripts\\update_fred_daily.py
"""

import sys
from pathlib import Path
from datetime import datetime

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from collectors.fred_data_manager import FredDataManager


def main():
    """Daily update of FRED data"""
    print(f"""
===============================================================
         FRED DATA DAILY UPDATE - {datetime.now().strftime('%Y-%m-%d %H:%M')}
===============================================================
    """)

    try:
        manager = FredDataManager()

        # Update last 7 days (incremental)
        print("[INFO] Updating FRED data (last 7 days)...")
        manager.update_recent_data(days_back=7)

        # Show stats
        stats = manager.get_database_stats()
        total_points = sum(stats.values())

        print(f"\n[OK] Update complete!")
        print(f"   Total data points in database: {total_points:,}")
        print(f"   Last update: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        # Success
        return 0

    except Exception as e:
        print(f"\n[ERROR] Update failed: {e}")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
