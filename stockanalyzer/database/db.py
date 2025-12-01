"""
STOCKANALYZER - Database Connection & Initialization

Ten moduł zarządza połączeniem z bazą danych SQLite:
- Tworzenie engine SQLAlchemy
- Tworzenie sesji
- Inicjalizacja tabel
- Helper functions dla operacji DB

Użycie:
    from database.db import init_database, get_session

    # Inicjalizacja (jeden raz przy starcie app)
    init_database()

    # Pobranie sesji do operacji
    session = get_session()
    analysis = session.query(Analysis).filter_by(ticker='AAPL').first()
    session.close()
"""

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.pool import StaticPool
from pathlib import Path

from database.models import Base, get_all_tables
from utils.config import Config


# ============================================
# DATABASE ENGINE
# ============================================

def get_database_url() -> str:
    """
    Zwraca URL połączenia z bazą danych.

    Returns:
        str: SQLite connection string

    Example:
        >>> url = get_database_url()
        >>> print(url)
        'sqlite:///C:/MEGABOT/stockanalyzer/stockanalyzer.db'
    """
    db_path = Config.DATABASE_PATH
    # SQLite wymaga formatu: sqlite:///path/to/db.db
    return f'sqlite:///{db_path}'


def create_database_engine():
    """
    Tworzy SQLAlchemy engine dla SQLite.

    Features:
    - WAL mode dla lepszej wydajności
    - Foreign keys enforcement
    - Connection pooling (StaticPool dla SQLite)

    Returns:
        Engine: SQLAlchemy engine object
    """
    url = get_database_url()

    # Create engine z custom settings
    engine = create_engine(
        url,
        echo=False,  # Set True dla debug SQL queries
        poolclass=StaticPool,  # StaticPool dla SQLite
        connect_args={'check_same_thread': False}  # Dla multi-threading (Streamlit)
    )

    # Enable WAL mode (Write-Ahead Logging) dla lepszej performance
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_conn, connection_record):
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA foreign_keys=ON")  # Enforce foreign keys
        cursor.close()

    return engine


# Global engine (singleton pattern)
_engine = None
_SessionFactory = None


def get_engine():
    """
    Pobiera globalny engine (singleton).

    Returns:
        Engine: SQLAlchemy engine
    """
    global _engine
    if _engine is None:
        _engine = create_database_engine()
    return _engine


def get_session_factory():
    """
    Pobiera session factory (singleton).

    Returns:
        sessionmaker: Factory do tworzenia sesji
    """
    global _SessionFactory
    if _SessionFactory is None:
        engine = get_engine()
        _SessionFactory = scoped_session(sessionmaker(bind=engine))
    return _SessionFactory


def get_session():
    """
    Tworzy nową sesję database.

    WAŻNE: Pamiętaj zamknąć sesję po użyciu!

    Returns:
        Session: SQLAlchemy session object

    Example:
        >>> session = get_session()
        >>> try:
        >>>     analysis = session.query(Analysis).first()
        >>>     print(analysis)
        >>> finally:
        >>>     session.close()
    """
    SessionFactory = get_session_factory()
    return SessionFactory()


# ============================================
# DATABASE INITIALIZATION
# ============================================

def init_database(drop_existing: bool = False):
    """
    Inicjalizuje bazę danych - tworzy wszystkie tabele.

    Args:
        drop_existing: Jeśli True, usuwa istniejące tabele (UWAGA: DESTRUCTIVE!)

    Example:
        >>> # Pierwsza inicjalizacja
        >>> init_database()

        >>> # Reset bazy (DEV ONLY!)
        >>> init_database(drop_existing=True)
    """
    engine = get_engine()

    if drop_existing:
        print("[WARNING] DROPPING all existing tables...")
        Base.metadata.drop_all(engine)

    print("Creating database tables...")
    Base.metadata.create_all(engine)

    # Verify tables created
    from sqlalchemy import inspect
    inspector = inspect(engine)
    tables = inspector.get_table_names()

    print(f"[OK] Database initialized at: {Config.DATABASE_PATH}")
    print(f"   Created {len(tables)} tables:")
    for table in tables:
        print(f"     - {table}")


def check_database_exists() -> bool:
    """
    Sprawdza czy baza danych już istnieje.

    Returns:
        bool: True jeśli plik DB istnieje
    """
    return Config.DATABASE_PATH.exists()


def get_database_stats() -> dict:
    """
    Zwraca statystyki bazy danych (ile rekordów w każdej tabeli).

    Returns:
        dict: {'table_name': count, ...}

    Example:
        >>> stats = get_database_stats()
        >>> print(f"Analyses: {stats['analyses']}")
    """
    from .models import Analysis, FredCache, StockCache, TwitterCache, UserPreferences, PdfExport, AppLog

    session = get_session()
    try:
        stats = {
            'analyses': session.query(Analysis).count(),
            'fred_cache': session.query(FredCache).count(),
            'stock_cache': session.query(StockCache).count(),
            'twitter_cache': session.query(TwitterCache).count(),
            'user_preferences': session.query(UserPreferences).count(),
            'pdf_exports': session.query(PdfExport).count(),
            'app_logs': session.query(AppLog).count(),
        }
        return stats
    finally:
        session.close()


# ============================================
# CONTEXT MANAGER (zalecane użycie)
# ============================================

class DatabaseSession:
    """
    Context manager dla sesji database - automatyczne zamykanie.

    Example:
        >>> with DatabaseSession() as session:
        >>>     analysis = session.query(Analysis).first()
        >>>     print(analysis)
        >>> # Session automatycznie zamknięta
    """

    def __enter__(self):
        self.session = get_session()
        return self.session

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            # W przypadku błędu - rollback
            self.session.rollback()
        self.session.close()


# ============================================
# TESTING & VALIDATION
# ============================================

if __name__ == "__main__":
    print("=" * 60)
    print("STOCKANALYZER - Database Initialization")
    print("=" * 60)

    # Check if DB exists
    if check_database_exists():
        print(f"[WARNING] Database already exists at: {Config.DATABASE_PATH}")
        print("   Use init_database(drop_existing=True) to reset")
    else:
        print("No database found. Creating new one...")

    # Initialize database
    init_database()

    # Show stats
    print("\nDatabase Statistics:")
    stats = get_database_stats()
    for table, count in stats.items():
        print(f"  {table}: {count} records")

    print("\n[OK] Database is ready!")
    print("=" * 60)
