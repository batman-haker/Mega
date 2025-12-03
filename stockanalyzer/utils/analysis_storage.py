"""
Analysis Storage Module
Handles saving and loading analysis history to SQLite database
"""

import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional


class AnalysisStorage:
    """Manages persistent storage of analysis history"""

    def __init__(self, db_path: str = "data/analysis_history.db"):
        """Initialize storage with database path"""
        self.db_path = Path(__file__).parent.parent / db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_database()

    def _init_database(self):
        """Create database tables if they don't exist"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS analyses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ticker TEXT NOT NULL,
                    timestamp DATETIME NOT NULL,
                    market_data TEXT NOT NULL,
                    experts TEXT NOT NULL,
                    opinions TEXT NOT NULL,
                    model_info TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Create index for faster ticker lookups
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_ticker
                ON analyses(ticker, timestamp DESC)
            """)

            conn.commit()

    def save_analysis(
        self,
        ticker: str,
        market_data: Dict,
        experts: List[str],
        opinions: List[Dict],
        model_info: Optional[str] = None
    ) -> int:
        """
        Save analysis to database

        Args:
            ticker: Stock ticker symbol
            market_data: Market data dictionary
            experts: List of expert names
            opinions: List of expert opinions
            model_info: Optional model information

        Returns:
            Analysis ID
        """
        timestamp = datetime.now().isoformat()

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                INSERT INTO analyses
                (ticker, timestamp, market_data, experts, opinions, model_info)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                ticker,
                timestamp,
                json.dumps(market_data),
                json.dumps(experts),
                json.dumps(opinions),
                model_info
            ))

            conn.commit()
            return cursor.lastrowid

    def get_recent_analyses(self, limit: int = 10) -> List[Dict]:
        """
        Get recent analyses

        Args:
            limit: Maximum number of analyses to return

        Returns:
            List of analysis dictionaries
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT * FROM analyses
                ORDER BY timestamp DESC
                LIMIT ?
            """, (limit,))

            return [dict(row) for row in cursor.fetchall()]

    def get_ticker_analyses(
        self,
        ticker: str,
        limit: int = 10
    ) -> List[Dict]:
        """
        Get analyses for specific ticker

        Args:
            ticker: Stock ticker symbol
            limit: Maximum number of analyses to return

        Returns:
            List of analysis dictionaries
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT * FROM analyses
                WHERE ticker = ?
                ORDER BY timestamp DESC
                LIMIT ?
            """, (ticker, limit))

            return [dict(row) for row in cursor.fetchall()]

    def get_analysis_by_id(self, analysis_id: int) -> Optional[Dict]:
        """
        Get analysis by ID

        Args:
            analysis_id: Analysis ID

        Returns:
            Analysis dictionary or None
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT * FROM analyses
                WHERE id = ?
            """, (analysis_id,))

            row = cursor.fetchone()
            return dict(row) if row else None

    def delete_analysis(self, analysis_id: int) -> bool:
        """
        Delete analysis by ID

        Args:
            analysis_id: Analysis ID

        Returns:
            True if deleted, False if not found
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                DELETE FROM analyses
                WHERE id = ?
            """, (analysis_id,))

            conn.commit()
            return cursor.rowcount > 0

    def get_statistics(self) -> Dict:
        """
        Get database statistics

        Returns:
            Dictionary with statistics
        """
        with sqlite3.connect(self.db_path) as conn:
            # Total analyses
            total = conn.execute(
                "SELECT COUNT(*) FROM analyses"
            ).fetchone()[0]

            # Unique tickers
            tickers = conn.execute(
                "SELECT COUNT(DISTINCT ticker) FROM analyses"
            ).fetchone()[0]

            # Most analyzed tickers
            top_tickers = conn.execute("""
                SELECT ticker, COUNT(*) as count
                FROM analyses
                GROUP BY ticker
                ORDER BY count DESC
                LIMIT 5
            """).fetchall()

            return {
                "total_analyses": total,
                "unique_tickers": tickers,
                "top_tickers": [
                    {"ticker": t[0], "count": t[1]}
                    for t in top_tickers
                ]
            }
