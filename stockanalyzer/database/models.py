"""
STOCKANALYZER - Database Models (SQLAlchemy ORM)

Definicje tabel bazy danych:
1. Analysis - Główne analizy AI
2. FredCache - Cache wskaźników FRED
3. StockCache - Cache danych giełdowych
4. TwitterCache - Cache sentymentu Twitter
5. UserPreferences - Ulubione eksperty i tickery
6. PdfExport - Historia eksportów PDF
7. AppLog - Logi aplikacji

Każda tabela ma:
- Jasno zdefiniowane kolumny z type hints
- Indexy dla szybkiego wyszukiwania
- Timestamps (created_at, updated_at)
- Docstringi z przykładami użycia
"""

from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Float, Text, Boolean,
    DateTime, ForeignKey, Index
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

# Base class dla wszystkich modeli
Base = declarative_base()


# ============================================
# MODEL 1: ANALYSIS
# ============================================

class Analysis(Base):
    """
    Główna tabela z analizami AI.

    Przechowuje kompletną analizę dla danego ticker + expert:
    - Dane makro (FRED)
    - Dane spółki (Yahoo Finance)
    - Sentiment Twitter
    - Rekomendacja AI
    - Scores

    Example:
        >>> analysis = Analysis(
        ...     ticker="AAPL",
        ...     expert_username="Dan_Kostecki",
        ...     combined_score=75.5,
        ...     ai_recommendation="BUY"
        ... )
        >>> session.add(analysis)
        >>> session.commit()
    """
    __tablename__ = 'analyses'

    # Primary key
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Identyfikatory
    ticker = Column(String(10), nullable=False, index=True)
    expert_username = Column(String(50), nullable=True)  # Nullable dla ogólnej analizy

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    last_refresh = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Data JSON (kompresja wszystkich danych)
    makro_data_json = Column(Text, nullable=True)
    stock_data_json = Column(Text, nullable=True)
    twitter_data_json = Column(Text, nullable=True)

    # Scores (-100 do +100)
    makro_score = Column(Float, nullable=True)
    stock_score = Column(Float, nullable=True)
    twitter_score = Column(Float, nullable=True)
    combined_score = Column(Float, nullable=True, index=True)

    # AI Results
    ai_recommendation = Column(String(20), nullable=True)  # STRONG_BUY, BUY, HOLD, SELL, STRONG_SELL
    ai_full_response = Column(Text, nullable=True)
    ai_model = Column(String(50), default='gemini-1.5-flash')

    # Metadata
    market_regime = Column(String(20), nullable=True)  # RISK_ON, RISK_OFF, CRISIS
    is_stale = Column(Boolean, default=False, index=True)

    # Relationships
    pdf_exports = relationship('PdfExport', back_populates='analysis', cascade='all, delete-orphan')

    def __repr__(self):
        return f"<Analysis(ticker={self.ticker}, expert={self.expert_username}, score={self.combined_score}, recommendation={self.ai_recommendation})>"


# Indexes dla Analysis
Index('idx_analysis_ticker_expert', Analysis.ticker, Analysis.expert_username)
Index('idx_analysis_created_desc', Analysis.created_at.desc())


# ============================================
# MODEL 2: FRED CACHE
# ============================================

class FredCache(Base):
    """
    Cache wskaźników FRED (makroekonomicznych).

    TTL: 1 godzina (dane FRED zmieniają się raz dziennie)

    Example:
        >>> fred = FredCache(
        ...     indicator_name="SOFR",
        ...     value=5.32,
        ...     value_change_pct=0.15,
        ...     valid_until=datetime.now() + timedelta(hours=1)
        ... )
    """
    __tablename__ = 'fred_cache'

    id = Column(Integer, primary_key=True, autoincrement=True)

    # Nazwa wskaźnika
    indicator_name = Column(String(50), nullable=False, index=True)

    # Wartości
    value = Column(Float, nullable=True)
    value_change_pct = Column(Float, nullable=True)  # Zmiana % vs poprzedni okres

    # Timestamps
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    valid_until = Column(DateTime, nullable=False, index=True)

    def __repr__(self):
        return f"<FredCache(indicator={self.indicator_name}, value={self.value}, valid_until={self.valid_until})>"


# Unique constraint: jeden wskaźnik w danym czasie
Index('idx_fred_unique', FredCache.indicator_name, FredCache.timestamp, unique=True)


# ============================================
# MODEL 3: STOCK CACHE
# ============================================

class StockCache(Base):
    """
    Cache danych giełdowych (Yahoo Finance).

    TTL: 15 minut (real-time quotes)

    Example:
        >>> stock = StockCache(
        ...     ticker="AAPL",
        ...     current_price=189.50,
        ...     fundamentals_json='{"pe_ratio": 28.5, ...}',
        ...     valid_until=datetime.now() + timedelta(minutes=15)
        ... )
    """
    __tablename__ = 'stock_cache'

    id = Column(Integer, primary_key=True, autoincrement=True)

    # Ticker
    ticker = Column(String(10), nullable=False, index=True)

    # Price data
    current_price = Column(Float, nullable=True)
    price_change_pct = Column(Float, nullable=True)

    # Full data JSON
    fundamentals_json = Column(Text, nullable=True)
    technicals_json = Column(Text, nullable=True)
    history_json = Column(Text, nullable=True)  # Price history (3mo)

    # Timestamps
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    valid_until = Column(DateTime, nullable=False, index=True)

    def __repr__(self):
        return f"<StockCache(ticker={self.ticker}, price={self.current_price}, valid_until={self.valid_until})>"


# Unique constraint
Index('idx_stock_unique', StockCache.ticker, StockCache.timestamp, unique=True)


# ============================================
# MODEL 4: TWITTER CACHE
# ============================================

class TwitterCache(Base):
    """
    Cache sentymentu Twitter.

    TTL: 30 minut

    Example:
        >>> twitter = TwitterCache(
        ...     expert_username="Dan_Kostecki",
        ...     ticker="AAPL",
        ...     sentiment_score=65.5,
        ...     tweets_json='[{"text": "...", ...}]',
        ...     valid_until=datetime.now() + timedelta(minutes=30)
        ... )
    """
    __tablename__ = 'twitter_cache'

    id = Column(Integer, primary_key=True, autoincrement=True)

    # Expert + Ticker
    expert_username = Column(String(50), nullable=False, index=True)
    ticker = Column(String(10), nullable=True)  # Nullable dla ogólnego sentymentu

    # Sentiment data
    sentiment_score = Column(Float, nullable=True)  # -100 do +100
    keyword_sentiment = Column(Float, nullable=True)  # Keyword-based
    llm_sentiment = Column(Float, nullable=True)  # Gemini-based

    # Tweets JSON
    tweets_json = Column(Text, nullable=True)
    tweet_count = Column(Integer, default=0)

    # Timestamps
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    valid_until = Column(DateTime, nullable=False, index=True)

    def __repr__(self):
        return f"<TwitterCache(expert={self.expert_username}, ticker={self.ticker}, sentiment={self.sentiment_score})>"


# Unique constraint
Index('idx_twitter_unique', TwitterCache.expert_username, TwitterCache.ticker, TwitterCache.timestamp, unique=True)


# ============================================
# MODEL 5: USER PREFERENCES
# ============================================

class UserPreferences(Base):
    """
    Preferencje użytkownika (ulubieni eksperci, tickery).

    Na przyszłość: multi-user support (user_id).

    Example:
        >>> prefs = UserPreferences(
        ...     user_id="default_user",
        ...     favorite_experts_json='["Dan_Kostecki", "T_Smolarek"]',
        ...     favorite_tickers_json='["AAPL", "MSFT"]'
        ... )
    """
    __tablename__ = 'user_preferences'

    id = Column(Integer, primary_key=True, autoincrement=True)

    # User ID (dla przyszłości - multi-user)
    user_id = Column(String(50), default='default_user', unique=True, nullable=False)

    # Favorites (JSON arrays)
    favorite_experts_json = Column(Text, nullable=True)  # ["Dan_Kostecki", ...]
    favorite_tickers_json = Column(Text, nullable=True)  # ["AAPL", "MSFT", ...]

    # Settings
    default_ai_model = Column(String(50), default='gemini-1.5-flash')
    language = Column(String(10), default='pl')

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<UserPreferences(user_id={self.user_id})>"


# ============================================
# MODEL 6: PDF EXPORT
# ============================================

class PdfExport(Base):
    """
    Historia eksportów PDF.

    Relationship: analysis_id → Analysis.id

    Example:
        >>> pdf = PdfExport(
        ...     analysis_id=123,
        ...     filename="AAPL_analysis_20251126.pdf",
        ...     file_path="C:\\MEGABOT\\stockanalyzer\\exports\\...",
        ...     file_size_kb=250
        ... )
    """
    __tablename__ = 'pdf_exports'

    id = Column(Integer, primary_key=True, autoincrement=True)

    # Foreign key do Analysis
    analysis_id = Column(Integer, ForeignKey('analyses.id', ondelete='CASCADE'), nullable=False, index=True)

    # File info
    filename = Column(String(255), nullable=False)
    file_path = Column(Text, nullable=False)
    file_size_kb = Column(Integer, nullable=True)

    # Timestamp
    generated_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationship
    analysis = relationship('Analysis', back_populates='pdf_exports')

    def __repr__(self):
        return f"<PdfExport(filename={self.filename}, analysis_id={self.analysis_id})>"


# ============================================
# MODEL 7: APP LOG
# ============================================

class AppLog(Base):
    """
    Logi aplikacji (opcjonalne - zamiast file logging).

    Levels: INFO, WARNING, ERROR

    Example:
        >>> log = AppLog(
        ...     level="ERROR",
        ...     message="Failed to fetch FRED data",
        ...     module="collectors.fred_collector"
        ... )
    """
    __tablename__ = 'app_logs'

    id = Column(Integer, primary_key=True, autoincrement=True)

    # Log data
    level = Column(String(10), nullable=False, index=True)  # INFO, WARNING, ERROR
    message = Column(Text, nullable=False)
    module = Column(String(100), nullable=True)  # Nazwa modułu Python

    # Timestamp
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    def __repr__(self):
        return f"<AppLog(level={self.level}, module={self.module}, time={self.timestamp})>"


# Index dla logów
Index('idx_logs_timestamp_desc', AppLog.timestamp.desc())
Index('idx_logs_level', AppLog.level)


# ============================================
# MODEL 8: FRED HISTORICAL DATA
# ============================================

class FredHistoricalData(Base):
    """
    Tabela przechowująca historyczne dane FRED.

    Zamiast pobierać 90 dni za każdym razem z API:
    - Raz pobieramy 365+ dni historii
    - Zapisujemy do tej tabeli
    - Codziennie aktualizujemy tylko najnowsze dane (7 dni)
    - FredCollector czyta z DB (instant!) zamiast z API

    Korzyści:
    - 100x szybsze ładowanie strony Makro
    - Oszczędność API limits (120 req/min → 1 req/day)
    - Pełna historia dla wykresów

    Example:
        >>> # Zapis danych
        >>> data_point = FredHistoricalData(
        ...     series_id='SOFR',
        ...     date=datetime(2024, 11, 28),
        ...     value=5.32
        ... )
        >>> session.add(data_point)

        >>> # Odczyt danych
        >>> sofr_history = session.query(FredHistoricalData).filter(
        ...     FredHistoricalData.series_id == 'SOFR',
        ...     FredHistoricalData.date >= datetime.now() - timedelta(days=90)
        ... ).order_by(FredHistoricalData.date).all()
    """
    __tablename__ = 'fred_historical_data'

    # Primary key
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Series identifiers
    series_id = Column(String(50), nullable=False, index=True)  # 'SOFR', 'VIX', 'WRESBAL', etc.

    # Data point
    date = Column(DateTime, nullable=False, index=True)
    value = Column(Float, nullable=False)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Constraints
    __table_args__ = (
        Index('idx_fred_hist_series_date', 'series_id', 'date', unique=True),
        Index('idx_fred_hist_date_desc', 'date', postgresql_using='btree', postgresql_ops={'date': 'DESC'}),
    )

    def __repr__(self):
        return f"<FredHistoricalData(series={self.series_id}, date={self.date.date()}, value={self.value})>"


# ============================================
# HELPER FUNCTIONS
# ============================================

def get_all_tables():
    """Zwraca listę wszystkich tabel (dla migracji)"""
    return [
        Analysis.__tablename__,
        FredCache.__tablename__,
        StockCache.__tablename__,
        TwitterCache.__tablename__,
        UserPreferences.__tablename__,
        PdfExport.__tablename__,
        AppLog.__tablename__,
        FredHistoricalData.__tablename__,
    ]


if __name__ == "__main__":
    print("STOCKANALYZER - Database Models")
    print("=" * 60)
    print("Defined tables:")
    for table in get_all_tables():
        print(f"  - {table}")
    print("=" * 60)
