# STOCKANALYZER - Master Roadmap & Architecture Plan

**Projekt:** AI-Powered Stock Analysis Web Application
**Data utworzenia:** 2025-11-26
**Status:** MASTER PLAN - Dokument niezmienialny
**Cel:** Kompleksowa aplikacja webowa do analizy akcji z wykorzystaniem danych makro, fundamentalnych i sentymentu ekspertów Twitter

---

## 📋 SPIS TREŚCI

1. [Przegląd Projektu](#1-przegląd-projektu)
2. [Decyzje Techniczne](#2-decyzje-techniczne)
3. [Architektura Systemu](#3-architektura-systemu)
4. [Schemat Bazy Danych](#4-schemat-bazy-danych)
5. [Struktura Plików](#5-struktura-plików)
6. [API Endpoints](#6-api-endpoints)
7. [Roadmapa Implementacji](#7-roadmapa-implementacji)
8. [Przewodnik Edukacyjny](#8-przewodnik-edukacyjny)
9. [MCP Integration Strategy](#9-mcp-integration-strategy)
10. [Design System - Cyberpunk Theme](#10-design-system-cyberpunk-theme)

---

## 1. PRZEGLĄD PROJEKTU

### 1.1 Wizja
STOCKANALYZER to profesjonalna aplikacja webowa łącząca dane makroekonomiczne (FRED), fundamenty spółek (Yahoo Finance) i sentiment ekspertów (Twitter) w jedną kompleksową analizę AI. Aplikacja wykorzystuje Gemini AI do generowania rekomendacji inwestycyjnych opartych na multi-source data fusion.

### 1.2 Główne Funkcje

**4 Podstrony Aplikacji:**

1. **MAKRO** - Analiza makroekonomiczna
   - Dane z projektu FRED (LiquidityMonitor)
   - Wskaźniki: liquidity, SOFR, spread, VIX, yield curve, M2, NFCI
   - Market regime detection (RISK_ON/RISK_OFF/CRISIS)
   - Wykresy czasowe i tabela z wartościami + zmiana %

2. **STOCK** - Analiza fundamentalna i techniczna spółek
   - Yahoo Finance jako jedyne źródło danych
   - Autocomplete ticker search (NYSE, NASDAQ, GPW)
   - Fundamentals: P/E, PEG, P/B, Debt/Equity, ROE, Profit Margin, Dividend Yield
   - Technicals: MA(20/50/200), RSI, MACD, Bollinger Bands
   - Price charts (candlestick/liniowe)

3. **TWITTER EXPERT ANALYZER** - Analiza sentymentu ekspertów
   - Lista ekspertów: Dan_Kostecki, T_Smolarek, hedgefundowiec, rditrych, ksochanek, HayekAndKeynes
   - Wybór eksperta + ticker
   - Dual analysis: Keyword-based + LLM (Gemini)
   - Gemini rate limit: 20 sek między zapytaniami (progress bar dla UX)
   - Timeline sentymentu w czasie

4. **AI ANALYSIS** - Kompleksowa analiza multi-source
   - Kombinacja: Makro + Stock + Twitter Sentiment
   - Super-prompt dla Gemini AI
   - Rekomendacja: STRONG_BUY/BUY/HOLD/SELL/STRONG_SELL
   - Strukturalna odpowiedź: justification, risk analysis, scenarios (bull/base/bear)
   - Export do PDF (WAŻNE!)

### 1.3 Kluczowe Wymagania

**Funkcjonalne:**
- Multi-page Streamlit app z routing
- Mobile-friendly responsive design
- Zapisywanie ulubionych ekspertów
- Cache + baza danych dla szybkości
- PDF export z pełną analizą
- Język: Polski (w przyszłości: Angielski)

**Niefunkcjonalne:**
- Cyberpunk design (dark theme, neon accents)
- Bez emoji i dziecinnych ikon (profesjonalny wygląd)
- Maksymalne wykorzystanie MCP servers
- Edukacyjna struktura kodu (komentarze, docstringi)
- Skalowalna architektura (łatwe dodawanie funkcji)

---

## 2. DECYZJE TECHNICZNE

### 2.1 Tech Stack - FINALNE DECYZJE

| Komponent | Technologia | Uzasadnienie |
|-----------|-------------|--------------|
| **Frontend Framework** | Streamlit 1.40.0+ | Szybki rozwój, native charts, multi-page support |
| **Backend Language** | Python 3.9+ | Ekosystem data science, obecny kod reusable |
| **Database** | SQLite → PostgreSQL | Start: SQLite (lokalny), Przyszłość: PostgreSQL (chmura) |
| **Makro Data** | FRED API + LiquidityMonitor | Projekt C:\FRED, wskaźniki liquidity |
| **Stock Data** | Yahoo Finance (yfinance) | Darmowy, reliabilny, GPW support |
| **Twitter Data** | Xscrap cache (JSON files) | Brak Twitter API (płatny), używamy istniejącego scraperа |
| **AI Analysis** | Google Gemini 1.5 Flash | Darmowy tier, rate limit: 20 sec |
| **Charts** | Plotly 5.18.0+ | Interaktywne, cyberpunk theming |
| **PDF Generation** | ReportLab 4.0+ | Pełna kontrola layoutu, custom styling |
| **MCP Servers** | 4 servers (filesystem, sequential-thinking, memory, gemini) | Enhanced capabilities |

### 2.2 API Keys & Rate Limits

```env
# Required API Keys (.env)
FRED_API_KEY=your_key_here          # Fred: 120 req/min, darmowy
GOOGLE_API_KEY=your_key_here        # Gemini: 20 sec między req, darmowy tier

# Optional (future)
ANTHROPIC_API_KEY=your_key_here     # Claude fallback
```

**Rate Limiting Strategy:**
- FRED: Cache na 1 godzinę (dane zmieniają się raz dziennie)
- Yahoo Finance: Cache na 15 minut (real-time quotes)
- Twitter Cache: Odświeżanie przez zewnętrzny Xscrap scraper
- Gemini AI: Enforced 20 sec delay + user progress indicator

### 2.3 Dependency List

```txt
# requirements.txt (zaktualizowane)
streamlit>=1.40.0
plotly>=5.18.0
pandas>=2.0.0
numpy>=1.24.0
yfinance>=0.2.28
requests>=2.31.0
google-generativeai>=0.8.3
python-dotenv>=1.0.0
python-dateutil>=2.8.2
reportlab>=4.0.0          # PDF generation
pillow>=10.0.0            # Image handling dla PDF
sqlalchemy>=2.0.0         # ORM dla bazy danych
```

---

## 3. ARCHITEKTURA SYSTEMU

### 3.1 High-Level Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                      STOCKANALYZER                              │
│                   Streamlit Multi-Page App                      │
└─────────────────────────────────────────────────────────────────┘
                              │
                ┌─────────────┴─────────────┐
                │                           │
        ┌───────▼────────┐         ┌────────▼───────┐
        │   UI Layer     │         │  Data Layer    │
        │  (Streamlit)   │         │  (Collectors)  │
        └───────┬────────┘         └────────┬───────┘
                │                           │
    ┌───────────┼───────────┬───────────────┼──────────┐
    │           │           │               │          │
┌───▼───┐  ┌───▼───┐  ┌────▼────┐    ┌─────▼─────┐   │
│ Makro │  │ Stock │  │ Twitter │    │ AI Analysis│   │
│ Page  │  │ Page  │  │ Page    │    │   Page     │   │
└───┬───┘  └───┬───┘  └────┬────┘    └─────┬──────┘   │
    │          │           │               │          │
    └──────────┴───────────┴───────────────┴──────────┘
                              │
                    ┌─────────▼──────────┐
                    │  Business Logic    │
                    │   (Services)       │
                    └─────────┬──────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
    ┌───▼────┐         ┌──────▼──────┐      ┌──────▼──────┐
    │ FRED   │         │ Yahoo       │      │  Gemini AI  │
    │ API    │         │ Finance API │      │     API     │
    └───┬────┘         └──────┬──────┘      └──────┬──────┘
        │                     │                     │
        └─────────────────────┼─────────────────────┘
                              │
                    ┌─────────▼──────────┐
                    │    Data Storage    │
                    │  SQLite Database   │
                    │  + Twitter Cache   │
                    └────────────────────┘
                              │
                    ┌─────────▼──────────┐
                    │   MCP Servers      │
                    │ • Filesystem       │
                    │ • Seq-Thinking     │
                    │ • Memory           │
                    │ • Gemini           │
                    └────────────────────┘
```

### 3.2 Data Flow - Complete Analysis

```
USER selects: Ticker="AAPL" + Expert="Dan_Kostecki"
    │
    ▼
Check Database: czy analiza istnieje i jest świeża (<1h)?
    │
    ├─► TAK → Pokaż z cache
    │
    └─► NIE → Rozpocznij nową analizę
            │
            ├─► Collector 1: FRED Data
            │   • LiquidityMonitor.get_all_indicators()
            │   • analyze_liquidity_conditions()
            │   • Cache na 1h
            │
            ├─► Collector 2: Yahoo Finance
            │   • yf.Ticker("AAPL").info
            │   • history(period="3mo")
            │   • Calculate technicals
            │   • Cache na 15min
            │
            ├─► Collector 3: Twitter Sentiment
            │   • Read Xscrap JSON cache
            │   • Filter by expert + ticker mentions
            │   • Keyword analysis (instant)
            │   • LLM analysis via Gemini (20 sec delay)
            │
            ├─► Combine Data
            │   • Weighted scoring: FRED(40%) + Stock(35%) + Twitter(25%)
            │   • Generate combined_score: -100 to +100
            │
            ├─► Build Super-Prompt
            │   • PromptBuilder.build_investment_prompt()
            │   • Include: Makro context + Stock fundamentals + Twitter sentiment
            │   • Structured questions for AI
            │
            ├─► Send to Gemini AI
            │   • Wait 20 sec (show progress bar)
            │   • Get recommendation + justification
            │   • Parse response
            │
            ├─► Save to Database
            │   • Insert into analyses table
            │   • Update cache tables
            │   • Generate PDF (optional)
            │
            └─► Display Results
                • Show recommendation
                • Expandable sections
                • Charts & metrics
                • PDF download button
```

### 3.3 Component Responsibilities

**UI Layer (Streamlit Pages):**
- `pages/1_Makro.py` - Wyświetla dane makro, wykresy FRED
- `pages/2_Stock.py` - Fundamentals, technicals, price charts
- `pages/3_Twitter.py` - Sentiment analysis, tweets timeline
- `pages/4_AI_Analysis.py` - Full analysis + AI recommendation
- `Home.py` - Landing page + navigation

**Data Layer (Collectors):**
- `collectors/fred_collector.py` - Integration z C:\FRED projekt
- `collectors/stock_collector.py` - Yahoo Finance API wrapper
- `collectors/twitter_collector.py` - Xscrap cache reader + Gemini sentiment

**Business Logic (Services):**
- `services/analysis_service.py` - Orchestration, scoring, caching
- `services/ai_service.py` - Gemini API, prompt building
- `services/pdf_service.py` - Report generation
- `services/cache_service.py` - Cache management, refresh logic

**Data Storage:**
- `database/models.py` - SQLAlchemy models
- `database/db.py` - Database connection, migrations
- SQLite file: `stockanalyzer.db`

**Utilities:**
- `utils/config.py` - Configuration management
- `utils/validators.py` - Input validation
- `utils/formatters.py` - Data formatting helpers

---

## 4. SCHEMAT BAZY DANYCH

### 4.1 SQLite Schema (Początkowa Wersja)

```sql
-- ============================================
-- STOCKANALYZER Database Schema v1.0
-- ============================================

-- Tabela 1: Główne analizy AI
CREATE TABLE analyses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ticker VARCHAR(10) NOT NULL,                  -- np. "AAPL"
    expert_username VARCHAR(50),                  -- np. "Dan_Kostecki" (nullable dla ogólnej analizy)

    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_refresh TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Data JSON (kompresja danych)
    makro_data_json TEXT,                         -- JSON z FRED indicators
    stock_data_json TEXT,                         -- JSON z Yahoo Finance
    twitter_data_json TEXT,                       -- JSON z Twitter sentiment

    -- Scores (-100 to +100)
    makro_score REAL,
    stock_score REAL,
    twitter_score REAL,
    combined_score REAL,

    -- AI Results
    ai_recommendation VARCHAR(20),                -- STRONG_BUY, BUY, HOLD, SELL, STRONG_SELL
    ai_full_response TEXT,                        -- Pełna odpowiedź AI (może być długa)
    ai_model VARCHAR(50) DEFAULT 'gemini-1.5-flash',

    -- Metadata
    market_regime VARCHAR(20),                    -- RISK_ON, RISK_OFF, CRISIS
    is_stale BOOLEAN DEFAULT 0,                   -- Czy dane są przestarzałe

    -- Indexes dla szybkiego wyszukiwania
    UNIQUE(ticker, expert_username, created_at)
);

CREATE INDEX idx_ticker ON analyses(ticker);
CREATE INDEX idx_created_at ON analyses(created_at DESC);
CREATE INDEX idx_stale ON analyses(is_stale);


-- Tabela 2: Cache wskaźników FRED
CREATE TABLE fred_cache (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    indicator_name VARCHAR(50) NOT NULL,          -- np. "SOFR", "VIX", "DXY"
    value REAL,
    value_change_pct REAL,                        -- Zmiana % vs poprzedni okres
    timestamp TIMESTAMP,
    valid_until TIMESTAMP,                        -- Cache expire time (now + 1h)

    UNIQUE(indicator_name, timestamp)
);

CREATE INDEX idx_fred_valid ON fred_cache(indicator_name, valid_until);


-- Tabela 3: Cache danych giełdowych
CREATE TABLE stock_cache (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ticker VARCHAR(10) NOT NULL,

    -- Price data
    current_price REAL,
    price_change_pct REAL,

    -- Full data JSON
    fundamentals_json TEXT,
    technicals_json TEXT,
    history_json TEXT,                            -- Price history (3mo)

    -- Cache control
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    valid_until TIMESTAMP,                        -- Cache expire (now + 15min)

    UNIQUE(ticker, timestamp)
);

CREATE INDEX idx_stock_valid ON stock_cache(ticker, valid_until);


-- Tabela 4: Cache Twitter sentiment
CREATE TABLE twitter_cache (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    expert_username VARCHAR(50) NOT NULL,
    ticker VARCHAR(10),                           -- Nullable - ogólny sentiment

    -- Sentiment data
    sentiment_score REAL,                         -- -100 to +100
    keyword_sentiment REAL,                       -- Keyword-based
    llm_sentiment REAL,                           -- Gemini-based (może być NULL jeśli nie użyty)

    -- Tweets JSON
    tweets_json TEXT,                             -- Array of tweet objects
    tweet_count INTEGER,

    -- Cache control
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    valid_until TIMESTAMP,                        -- Cache expire (now + 30min)

    UNIQUE(expert_username, ticker, timestamp)
);

CREATE INDEX idx_twitter_valid ON twitter_cache(expert_username, ticker, valid_until);


-- Tabela 5: User Preferences
CREATE TABLE user_preferences (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id VARCHAR(50) DEFAULT 'default_user',   -- Dla przyszłości (multi-user)

    -- Favorites
    favorite_experts_json TEXT,                   -- JSON array: ["Dan_Kostecki", "T_Smolarek"]
    favorite_tickers_json TEXT,                   -- JSON array: ["AAPL", "MSFT", "PKO.WA"]

    -- Settings
    default_ai_model VARCHAR(50) DEFAULT 'gemini-1.5-flash',
    language VARCHAR(10) DEFAULT 'pl',            -- 'pl' lub 'en'

    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(user_id)
);


-- Tabela 6: PDF Exports History
CREATE TABLE pdf_exports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    analysis_id INTEGER NOT NULL,                 -- Foreign key → analyses.id

    filename VARCHAR(255),                        -- np. "AAPL_analysis_20251126.pdf"
    file_path TEXT,                               -- Pełna ścieżka do pliku
    file_size_kb INTEGER,

    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (analysis_id) REFERENCES analyses(id) ON DELETE CASCADE
);

CREATE INDEX idx_pdf_analysis ON pdf_exports(analysis_id);


-- Tabela 7: Application Logs (opcjonalna)
CREATE TABLE app_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    level VARCHAR(10),                            -- INFO, WARNING, ERROR
    message TEXT,
    module VARCHAR(100),                          -- Nazwa modułu Python
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_logs_timestamp ON app_logs(timestamp DESC);
CREATE INDEX idx_logs_level ON app_logs(level);
```

### 4.2 Cache Refresh Logic

```python
# Pseudo-kod dla cache management

def get_fred_data():
    cached = db.query(fred_cache).filter(
        fred_cache.valid_until > now()
    ).first()

    if cached:
        return cached.data
    else:
        fresh_data = fetch_from_fred_api()
        db.insert(fred_cache, data=fresh_data, valid_until=now()+1h)
        return fresh_data

def get_analysis(ticker, expert):
    analysis = db.query(analyses).filter(
        ticker=ticker,
        expert=expert,
        last_refresh > now() - 1h  # Fresh jeśli < 1h
    ).first()

    if analysis:
        return analysis
    else:
        return create_new_analysis(ticker, expert)
```

---

## 5. STRUKTURA PLIKÓW

### 5.1 Directory Layout

```
C:\MEGABOT\
│
├── stockanalyzer/                    # Nowy główny katalog aplikacji
│   │
│   ├── Home.py                       # Streamlit entry point (landing page)
│   │
│   ├── pages/                        # Streamlit multi-page
│   │   ├── 1_📊_Makro.py
│   │   ├── 2_📈_Stock.py
│   │   ├── 3_🐦_Twitter.py
│   │   └── 4_🤖_AI_Analysis.py
│   │
│   ├── collectors/                   # Data collection modules
│   │   ├── __init__.py
│   │   ├── fred_collector.py        # FRED API + LiquidityMonitor integration
│   │   ├── stock_collector.py       # Yahoo Finance wrapper
│   │   └── twitter_collector.py     # Xscrap cache + Gemini sentiment
│   │
│   ├── services/                     # Business logic
│   │   ├── __init__.py
│   │   ├── analysis_service.py      # Main orchestrator
│   │   ├── ai_service.py            # Gemini API integration
│   │   ├── pdf_service.py           # PDF generation
│   │   ├── cache_service.py         # Cache management
│   │   └── scoring_service.py       # Score calculation logic
│   │
│   ├── database/                     # Database layer
│   │   ├── __init__.py
│   │   ├── models.py                # SQLAlchemy models
│   │   ├── db.py                    # Database connection
│   │   └── migrations/              # DB migrations (future)
│   │
│   ├── utils/                        # Utilities
│   │   ├── __init__.py
│   │   ├── config.py                # Configuration management
│   │   ├── validators.py            # Input validation
│   │   ├── formatters.py            # Data formatting
│   │   └── constants.py             # Constants (expert list, thresholds)
│   │
│   ├── components/                   # Reusable Streamlit components
│   │   ├── __init__.py
│   │   ├── charts.py                # Chart components (Plotly wrappers)
│   │   ├── metrics.py               # Metric display components
│   │   ├── tables.py                # Table formatters
│   │   └── cyberpunk_theme.py       # Custom CSS + styling
│   │
│   ├── static/                       # Static assets
│   │   ├── css/
│   │   │   └── cyberpunk.css        # Custom Streamlit CSS
│   │   ├── images/
│   │   │   ├── logo.png
│   │   │   └── background.png
│   │   └── fonts/
│   │       └── Orbitron-Regular.ttf
│   │
│   ├── exports/                      # Generated PDFs
│   │   └── .gitkeep
│   │
│   ├── stockanalyzer.db              # SQLite database
│   ├── requirements.txt              # Python dependencies
│   ├── .env                          # API keys (gitignored)
│   ├── .env.example                  # Environment template
│   └── README.md                     # Stockanalyzer documentation
│
├── data/                             # Legacy MEGABOT data (keep for now)
├── logs/                             # Application logs
├── .claude/                          # MCP configuration
│   └── settings.local.json
│
└── STOCKANALYZER_ROADMAP.md          # This file
```

### 5.2 File Responsibilities

**Home.py** (Landing Page)
- Welcome screen z logo
- Krótki opis aplikacji
- Navigation do 4 podstron
- Quick stats (ile analiz w DB, ostatnia aktualizacja)

**pages/1_📊_Makro.py**
- Display FRED indicators
- Regime detection box
- Time-series charts (Plotly)
- Table: indicator | value | change % | interpretation

**pages/2_📈_Stock.py**
- Ticker search autocomplete
- Company info header (name, sector, price)
- 2-column layout: Fundamentals | Technicals
- Price chart (candlestick)
- Score gauge meter

**pages/3_🐦_Twitter.py**
- Expert dropdown
- Ticker input
- Analyze button (with 20 sec progress bar for Gemini)
- Results: Keyword sentiment + LLM sentiment + tweets list
- Timeline chart (sentiment over time)

**pages/4_🤖_AI_Analysis.py**
- Ticker + Expert selection
- "Run Analysis" button
- Loading spinner (może trwać 30-60 sec)
- Results display:
  - Main recommendation (BUY/HOLD/SELL)
  - Expandable sections (Makro, Stock, Twitter, AI Response)
  - Scenarios (Bull/Base/Bear)
  - PDF download button

---

## 6. API ENDPOINTS

### 6.1 Internal API Functions

Chociaż Streamlit nie wymaga REST API, tworzymy wewnętrzne funkcje jako "pseudo-API" dla separation of concerns:

**collectors/fred_collector.py**
```python
def get_fred_indicators() -> dict:
    """
    Returns: {
        'indicators': [{'name': 'SOFR', 'value': 5.32, 'change_pct': 0.15}, ...],
        'regime': 'RISK_ON',
        'score': 65,
        'alerts': ['High VIX detected'],
        'timestamp': '2025-11-26T10:00:00Z'
    }
    """

def get_liquidity_analysis() -> dict:
    """
    Calls LiquidityMonitor from C:\FRED project
    Returns full liquidity analysis
    """
```

**collectors/stock_collector.py**
```python
def get_stock_data(ticker: str) -> dict:
    """
    Returns: {
        'ticker': 'AAPL',
        'company_name': 'Apple Inc.',
        'current_price': 189.50,
        'fundamentals': {...},
        'technicals': {...},
        'history': [...],
        'score': 72
    }
    """

def search_tickers(query: str, exchanges: list) -> list:
    """
    Autocomplete search
    Args: query='app', exchanges=['NYSE', 'NASDAQ', 'GPW']
    Returns: [{'ticker': 'AAPL', 'name': 'Apple Inc.'}, ...]
    """
```

**collectors/twitter_collector.py**
```python
def get_twitter_sentiment(expert: str, ticker: str = None) -> dict:
    """
    Returns: {
        'expert': 'Dan_Kostecki',
        'ticker': 'AAPL',
        'keyword_sentiment': 45,
        'llm_sentiment': 52,  # Gemini analysis
        'combined_sentiment': 48.5,
        'tweets': [...],
        'tweet_count': 15
    }
    """

def analyze_tweets_with_gemini(tweets: list, ticker: str) -> dict:
    """
    Send tweets to Gemini for sentiment analysis
    IMPORTANT: 20 sec rate limit enforced
    """
```

**services/analysis_service.py**
```python
def create_full_analysis(ticker: str, expert: str = None) -> dict:
    """
    Main orchestrator - combines all data sources
    Returns complete analysis object
    """

def get_or_refresh_analysis(ticker: str, expert: str, max_age_hours: int = 1) -> dict:
    """
    Check DB for existing analysis, refresh if stale
    """
```

**services/ai_service.py**
```python
def build_super_prompt(analysis_data: dict) -> str:
    """
    Build comprehensive prompt for Gemini
    """

def get_ai_recommendation(prompt: str) -> dict:
    """
    Call Gemini API, parse response
    Returns: {
        'recommendation': 'BUY',
        'justification': '...',
        'risk_level': 'MEDIUM',
        'scenarios': {...}
    }
    """
```

**services/pdf_service.py**
```python
def generate_pdf_report(analysis_id: int) -> str:
    """
    Generate PDF from analysis
    Returns: filepath to generated PDF
    """
```

---

## 7. ROADMAPA IMPLEMENTACJI

### 7.1 Faza 1: Foundation & Setup (Sesja 1-2)

**Cel:** Przygotować środowisko, strukturę projektu i bazę danych

**Kroki:**
1. Utworzyć strukturę katalogów `stockanalyzer/`
2. Setup requirements.txt z wszystkimi dependencies
3. Konfiguracja .env (API keys)
4. Utworzyć database schema (SQLite)
   - Napisać models.py (SQLAlchemy)
   - Utworzyć db.py (connection + init)
   - Test: Połączenie z bazą, tworzenie tabel
5. Setup utils/config.py
6. Utworzyć Home.py (landing page - prosty)
7. Test: `streamlit run Home.py` - aplikacja się uruchamia

**Nauka:**
- Struktura projektu Python (packages, modules)
- SQLAlchemy ORM basics
- Streamlit multi-page apps
- Environment variables

**Rezultat:** Działająca pusta aplikacja, gotowa baza danych

---

### 7.2 Faza 2: Makro Page (Sesja 3-4)

**Cel:** Pierwsza funkcjonalna podstrona z danymi FRED

**Kroki:**
1. Napisać `collectors/fred_collector.py`
   - Integration z C:\FRED LiquidityMonitor
   - get_fred_indicators()
   - Cache logic (SQLite fred_cache table)
2. Napisać `pages/1_📊_Makro.py`
   - Display indicators w tabeli
   - Regime detection box
   - Plotly charts (time series)
3. Napisać `components/charts.py`
   - Reusable chart functions
4. Napisać `components/cyberpunk_theme.py`
   - Custom CSS dla Streamlit
   - Dark theme, neon colors
5. Test: Makro page z prawdziwymi danymi FRED

**Nauka:**
- Integracja z zewnętrznymi projektami Python
- Plotly charts (line, area)
- Streamlit layout (columns, expanders)
- CSS customization w Streamlit
- Cache management

**Rezultat:** Działająca Makro page z wykresami i tabelami

---

### 7.3 Faza 3: Stock Page (Sesja 5-6)

**Cel:** Podstrona z danymi giełdowymi (Yahoo Finance)

**Kroki:**
1. Napisać `collectors/stock_collector.py`
   - Yahoo Finance API wrapper (yfinance)
   - get_stock_data(ticker)
   - search_tickers(query) - autocomplete
   - Cache logic (stock_cache table)
2. Napisać `services/scoring_service.py`
   - Calculate fundamentals score
   - Calculate technicals score
   - Combined stock score (-100 to +100)
3. Napisać `pages/2_📈_Stock.py`
   - Ticker autocomplete input
   - Company info header
   - Fundamentals table (2 columns)
   - Technicals table (2 columns)
   - Price candlestick chart
   - Score gauge meter
4. Napisać `components/metrics.py`
   - Reusable metric display components
5. Test: Stock page z AAPL, MSFT, PKO.WA

**Nauka:**
- Yahoo Finance API (yfinance library)
- Financial indicators calculation
- Candlestick charts (Plotly)
- Streamlit input widgets (selectbox, text_input)
- Autocomplete implementation

**Rezultat:** Działająca Stock page z real-time danymi

---

### 7.4 Faza 4: Twitter Page (Sesja 7-8)

**Cel:** Analiza sentymentu ekspertów Twitter

**Kroki:**
1. Napisać `collectors/twitter_collector.py`
   - Read Xscrap JSON cache
   - Filter tweets by expert + ticker
   - Keyword-based sentiment analysis
   - Gemini LLM sentiment (z 20 sec delay)
   - Cache logic (twitter_cache table)
2. Napisać `utils/constants.py`
   - Lista ekspertów
   - Bullish/bearish keywords
   - Scoring thresholds
3. Napisać `pages/3_🐦_Twitter.py`
   - Expert dropdown
   - Ticker input
   - Analyze button
   - Progress bar (20 sec Gemini wait)
   - Display: keyword sentiment + LLM sentiment
   - Tweets list (najnowsze 20)
   - Timeline chart (sentiment w czasie)
4. Test: Twitter sentiment dla Dan_Kostecki + AAPL

**Nauka:**
- JSON parsing (Twitter data)
- Keyword matching algorithms
- Gemini API integration
- Rate limiting (20 sec delay)
- Progress indicators w Streamlit
- Time-series sentiment analysis

**Rezultat:** Działająca Twitter page z dual sentiment

---

### 7.5 Faza 5: AI Analysis Page (Sesja 9-11)

**Cel:** Kompleksowa analiza AI z wszystkimi źródłami danych

**Kroki:**
1. Napisać `services/analysis_service.py`
   - create_full_analysis(ticker, expert)
   - Orchestrate: FRED + Stock + Twitter
   - Calculate combined score
   - Save to analyses table
   - get_or_refresh_analysis() - cache logic
2. Napisać `services/ai_service.py`
   - build_super_prompt(analysis_data)
   - get_ai_recommendation(prompt)
   - Gemini API call (z 20 sec delay)
   - Parse AI response
3. Napisać `pages/4_🤖_AI_Analysis.py`
   - Ticker + Expert selection
   - "Run Analysis" button
   - Loading spinner (może trwać 60+ sec)
   - Results display:
     - Main recommendation badge (BUY/HOLD/SELL)
     - Score metrics (4 cards: Makro, Stock, Twitter, Combined)
     - Expandable sections:
       - Makro context
       - Stock analysis
       - Twitter sentiment
       - AI full response
     - Scenarios table (Bull/Base/Bear)
     - Risk analysis
4. Test: Full analysis dla AAPL + Dan_Kostecki

**Nauka:**
- Orchestration patterns
- Complex prompt engineering
- Gemini AI API advanced usage
- Streamlit advanced layouts (tabs, expanders)
- Multi-source data fusion
- Score aggregation logic

**Rezultat:** Działająca AI Analysis page z rekomendacjami

---

### 7.6 Faza 6: PDF Export (Sesja 12-13)

**Cel:** Profesjonalne raporty PDF

**Kroki:**
1. Napisać `services/pdf_service.py`
   - generate_pdf_report(analysis_id)
   - ReportLab layout:
     - Header (logo, ticker, data)
     - Makro summary section
     - Stock data section (tabela + chart jako image)
     - Twitter sentiment section
     - AI recommendation section (full text)
     - Scenarios table
     - Footer (disclaimer)
   - Cyberpunk styling (dark BG, neon headers)
   - Save to exports/ directory
   - Insert record do pdf_exports table
2. Dodać do `pages/4_🤖_AI_Analysis.py`
   - "Download PDF" button
   - Generate on-demand
   - Streamlit download_button
3. Test: Generate PDF dla pełnej analizy

**Nauka:**
- ReportLab library (PDF generation)
- PDF layout design
- Image embedding (charts → PDF)
- File handling w Streamlit
- Download functionality

**Rezultat:** Export PDF z pełną analizą

---

### 7.7 Faza 7: User Preferences (Sesja 14)

**Cel:** Zapisywanie ulubionych ekspertów i tickerów

**Kroki:**
1. Dodać do `Home.py`:
   - Sidebar: Ulubieni eksperci (multiselect)
   - Sidebar: Ulubione tickery (multiselect)
   - Save button → zapisz do user_preferences table
2. Dodać do innych pages:
   - Quick select z ulubionych
   - "Add to favorites" button
3. Test: Zapisywanie i wczytywanie preferencji

**Nauka:**
- User state management
- Database CRUD operations
- Streamlit session_state
- Persistent preferences

**Rezultat:** Działające user preferences

---

### 7.8 Faza 8: Polish & Optimization (Sesja 15-16)

**Cel:** Finalizacja, optymalizacja, dokumentacja

**Kroki:**
1. Cyberpunk theme refinement
   - Dopracować CSS
   - Dodać animacje (subtle)
   - Glitch effect na logo
2. Performance optimization
   - Cache tuning
   - Query optimization
   - Lazy loading dla danych
3. Error handling
   - Try/catch we wszystkich API calls
   - User-friendly error messages
   - Fallback strategies
4. Documentation
   - Docstrings we wszystkich funkcjach
   - README.md dla stockanalyzer/
   - Komentarze w kodzie (edukacyjne)
5. Testing
   - Manual testing wszystkich flow
   - Edge cases (brak danych, API errors)
6. Deployment prep
   - .streamlit/config.toml
   - Secrets management
   - Production .env

**Nauka:**
- Code documentation best practices
- Error handling patterns
- Performance optimization
- Production deployment prep

**Rezultat:** Production-ready aplikacja

---

### 7.9 Faza 9: Future Enhancements (Backlog)

**Opcjonalne rozszerzenia (po zakończeniu core features):**

1. **Multi-language support**
   - Dodać EN translation
   - i18n system

2. **Advanced charting**
   - Technical indicators overlays (MACD, Bollinger)
   - Comparison charts (multiple stocks)

3. **Portfolio mode**
   - Analyze multiple stocks as portfolio
   - Correlation matrix
   - Diversification score

4. **Alert system**
   - Email notifications
   - Discord webhooks
   - Price alerts, regime change alerts

5. **Backtesting**
   - Historical analysis replay
   - Performance metrics

6. **Cloud deployment**
   - Migrate SQLite → PostgreSQL
   - Deploy na Streamlit Cloud / Railway
   - CI/CD pipeline

7. **API endpoint**
   - FastAPI wrapper
   - REST API dla zewnętrznych aplikacji

---

## 8. PRZEWODNIK EDUKACYJNY

### 8.1 Zasady Edukacyjne Projektu

Każda sesja implementacji będzie miała:

1. **Wprowadzenie teoretyczne (5-10 min)**
   - Co będziemy budować
   - Jakie technologie użyjemy
   - Dlaczego tak, a nie inaczej

2. **Implementacja krok po kroku (30-45 min)**
   - Live coding z wyjaśnieniami
   - Komentarze w kodzie (PL)
   - Docstrings (EN) dla profesjonalizmu

3. **Testing & Debugging (10-15 min)**
   - Uruchomienie kodu
   - Debugowanie błędów
   - Best practices

4. **Podsumowanie & Next Steps (5 min)**
   - Co zrobiliśmy
   - Co nauczyliśmy się
   - Co będzie w następnej sesji

### 8.2 Kluczowe Koncepty do Nauki

**Python:**
- Klasy i OOP
- Type hints (mypy)
- Context managers
- Decorators
- Async/await (opcjonalnie)

**Data Science:**
- Pandas DataFrames
- NumPy arrays
- Data cleaning & validation
- Statistical calculations

**Streamlit:**
- Multi-page apps
- Session state management
- Caching (@st.cache_data)
- Custom components
- Layout (columns, tabs, expanders)

**Database:**
- SQL basics (SELECT, INSERT, UPDATE)
- SQLAlchemy ORM
- Migrations
- Indexing strategies

**APIs:**
- REST API consumption
- Rate limiting
- Error handling
- JSON parsing

**AI/ML:**
- Prompt engineering
- LLM APIs (Gemini)
- Sentiment analysis
- Score aggregation

**Software Engineering:**
- Project structure
- Separation of concerns
- DRY principle
- Configuration management
- Logging
- Documentation

### 8.3 Kod Style Guide

**Naming Conventions:**
- Variables: `snake_case`
- Functions: `snake_case`
- Classes: `PascalCase`
- Constants: `UPPER_SNAKE_CASE`
- Private: `_leading_underscore`

**Docstrings (Google Style):**
```python
def get_stock_data(ticker: str, period: str = "3mo") -> dict:
    """
    Fetch stock data from Yahoo Finance with caching.

    Args:
        ticker: Stock ticker symbol (e.g., "AAPL")
        period: Historical data period (default: "3mo")

    Returns:
        Dictionary containing:
            - ticker: str
            - current_price: float
            - fundamentals: dict
            - technicals: dict
            - history: list

    Raises:
        ValueError: If ticker is invalid
        requests.RequestException: If API call fails

    Example:
        >>> data = get_stock_data("AAPL")
        >>> print(data['current_price'])
        189.50
    """
```

**Komentarze (Polski dla edukacji):**
```python
# Sprawdzamy cache - jeśli dane są świeże (< 15 min), zwracamy z cache
cached = get_from_cache(ticker)
if cached and cached.is_fresh():
    return cached.data

# Brak cache lub stare dane - pobieramy świeże z API
fresh_data = fetch_from_yahoo_finance(ticker)

# Zapisujemy do cache na przyszłość (valid przez 15 min)
save_to_cache(ticker, fresh_data, ttl=15*60)
```

---

## 9. MCP INTEGRATION STRATEGY

### 9.1 MCP Servers Usage Plan

**Filesystem MCP:**
```python
# Przykład: Użycie MCP do zapisywania/czytania z bazy
# (przez MCP filesystem zamiast bezpośrednio)

def save_analysis_via_mcp(analysis_data: dict):
    # MCP filesystem zapewnia lepszy error handling i logging
    mcp_filesystem.write_json(
        path="stockanalyzer.db",  # lub JSON export
        data=analysis_data
    )
```

**Sequential-Thinking MCP:**
```python
# Przykład: Budowanie super-promptu z structured reasoning

def build_super_prompt_with_mcp(analysis_data: dict) -> str:
    # MCP sequential-thinking pomaga w strukturyzacji promptu
    thought_process = mcp_sequential_thinking.think_step_by_step([
        "Analyze macroeconomic context",
        "Evaluate stock fundamentals",
        "Assess Twitter sentiment",
        "Synthesize recommendation"
    ], context=analysis_data)

    # Używamy thought_process do budowy lepszego promptu
    return construct_prompt(thought_process)
```

**Memory MCP:**
```python
# Przykład: Zapamiętywanie user preferences i past analyses

def remember_user_preference(key: str, value: any):
    mcp_memory.create_entity(
        type="user_preference",
        name=key,
        observations=[f"User prefers {value}"]
    )

def get_analysis_insights(ticker: str):
    # MCP memory pamięta poprzednie analizy
    past_insights = mcp_memory.search_nodes(
        query=f"previous analyses of {ticker}"
    )
    return past_insights
```

**Gemini MCP:**
```python
# Przykład: Bezpośrednie zapytania AI przez MCP (zamiast google-generativeai)

def get_ai_recommendation_via_mcp(prompt: str) -> str:
    response = mcp_gemini.generate_content(
        prompt=prompt,
        model="gemini-1.5-flash",
        temperature=0.3
    )
    return response.text
```

### 9.2 MCP Benefits dla Projektu

1. **Better Error Handling** - MCP servers mają built-in retry logic
2. **Logging & Monitoring** - Automatyczne logowanie wszystkich operacji
3. **Caching** - MCP może cache'ować odpowiedzi
4. **Structured Output** - MCP wymusza strukturę danych
5. **Future-Proof** - Łatwa zmiana backendu (np. Gemini → Claude)

---

## 10. DESIGN SYSTEM - CYBERPUNK THEME

### 10.1 Color Palette

```css
/* Primary Colors */
--bg-dark: #0a0e27;           /* Main background */
--bg-card: #1a1a2e;           /* Card background */
--bg-hover: #252547;          /* Hover state */

/* Accent Colors */
--neon-cyan: #00f5ff;         /* Primary accent */
--neon-magenta: #ff006e;      /* Secondary accent */
--neon-green: #39ff14;        /* Success/positive */
--neon-red: #ff073a;          /* Error/negative */
--neon-yellow: #ffed4e;       /* Warning */

/* Text Colors */
--text-primary: #e0e0e0;      /* Main text */
--text-secondary: #a0a0a0;    /* Secondary text */
--text-dim: #606060;          /* Dim text */

/* Chart Colors */
--chart-line-up: #39ff14;     /* Upward trends */
--chart-line-down: #ff073a;   /* Downward trends */
--chart-line-neutral: #00f5ff; /* Neutral */
```

### 10.2 Typography

```css
/* Fonts */
--font-header: 'Orbitron', sans-serif;     /* Headers - futuristic */
--font-body: 'Roboto', sans-serif;         /* Body text - readable */
--font-mono: 'Share Tech Mono', monospace; /* Code/numbers */

/* Sizes */
--text-xs: 0.75rem;
--text-sm: 0.875rem;
--text-base: 1rem;
--text-lg: 1.125rem;
--text-xl: 1.25rem;
--text-2xl: 1.5rem;
--text-3xl: 2rem;
```

### 10.3 Components

**Neon Card:**
```css
.neon-card {
    background: var(--bg-card);
    border: 2px solid var(--neon-cyan);
    border-radius: 8px;
    box-shadow: 0 0 20px rgba(0, 245, 255, 0.3);
    padding: 1.5rem;
}
```

**Glitch Text (Logo):**
```css
.glitch {
    font-family: var(--font-header);
    color: var(--neon-cyan);
    text-shadow:
        0 0 10px var(--neon-cyan),
        0 0 20px var(--neon-cyan),
        0 0 30px var(--neon-magenta);
    animation: glitch 2s infinite;
}
```

**Scan Line Background:**
```css
body::before {
    content: '';
    position: fixed;
    top: 0; left: 0; right: 0; bottom: 0;
    background: repeating-linear-gradient(
        0deg,
        rgba(0, 245, 255, 0.03) 0px,
        rgba(0, 245, 255, 0.03) 1px,
        transparent 1px,
        transparent 2px
    );
    pointer-events: none;
    z-index: 1000;
}
```

**Metric Badge:**
```css
.metric-positive {
    background: rgba(57, 255, 20, 0.1);
    border: 1px solid var(--neon-green);
    color: var(--neon-green);
}

.metric-negative {
    background: rgba(255, 7, 58, 0.1);
    border: 1px solid var(--neon-red);
    color: var(--neon-red);
}
```

### 10.4 Streamlit Custom CSS

```python
# components/cyberpunk_theme.py

def load_cyberpunk_theme():
    """Apply cyberpunk CSS to Streamlit app"""
    st.markdown("""
    <style>
        /* Import fonts */
        @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Roboto:wght@300;400;700&family=Share+Tech+Mono&display=swap');

        /* Main app background */
        .stApp {
            background: linear-gradient(135deg, #0a0e27 0%, #1a1a2e 100%);
            font-family: 'Roboto', sans-serif;
            color: #e0e0e0;
        }

        /* Headers */
        h1, h2, h3 {
            font-family: 'Orbitron', sans-serif;
            color: #00f5ff;
            text-shadow: 0 0 10px rgba(0, 245, 255, 0.5);
        }

        /* Cards/Containers */
        .element-container {
            background: rgba(26, 26, 46, 0.6);
            border: 1px solid rgba(0, 245, 255, 0.2);
            border-radius: 8px;
            padding: 1rem;
        }

        /* Buttons */
        .stButton>button {
            background: linear-gradient(90deg, #00f5ff, #00d4ff);
            color: #0a0e27;
            border: 2px solid #00f5ff;
            border-radius: 4px;
            font-family: 'Orbitron', sans-serif;
            font-weight: 700;
            box-shadow: 0 0 20px rgba(0, 245, 255, 0.4);
            transition: all 0.3s ease;
        }

        .stButton>button:hover {
            box-shadow: 0 0 30px rgba(0, 245, 255, 0.8);
            transform: translateY(-2px);
        }

        /* Metrics */
        [data-testid="stMetricValue"] {
            font-family: 'Share Tech Mono', monospace;
            color: #00f5ff;
            font-size: 2rem;
        }

        /* Sidebar */
        .css-1d391kg {
            background: rgba(10, 14, 39, 0.95);
            border-right: 2px solid rgba(0, 245, 255, 0.3);
        }

        /* Input fields */
        .stTextInput>div>div>input {
            background: rgba(26, 26, 46, 0.8);
            border: 1px solid #00f5ff;
            color: #e0e0e0;
            border-radius: 4px;
        }

        /* Plotly charts - dark theme */
        .js-plotly-plot {
            background: transparent !important;
        }

        /* Scan lines effect */
        .stApp::before {
            content: '';
            position: fixed;
            top: 0; left: 0; right: 0; bottom: 0;
            background: repeating-linear-gradient(
                0deg,
                rgba(0, 245, 255, 0.03) 0px,
                rgba(0, 245, 255, 0.03) 1px,
                transparent 1px,
                transparent 2px
            );
            pointer-events: none;
            z-index: 1000;
        }
    </style>
    """, unsafe_allow_html=True)
```

---

## 11. FINALNE UWAGI

### 11.1 Success Criteria

Projekt będzie uznany za ukończony (MVP), gdy:

- [ ] Wszystkie 4 podstrony działają
- [ ] Dane z FRED/Yahoo/Twitter są poprawnie pobierane
- [ ] AI analiza generuje sensowne rekomendacje
- [ ] Baza danych zapisuje i cache'uje wyniki
- [ ] PDF export działa
- [ ] User preferences są zapisywane
- [ ] Cyberpunk design jest spójny
- [ ] Aplikacja jest mobile-friendly
- [ ] Kod jest udokumentowany (docstrings + komentarze)
- [ ] Wszystkie MCP servers są wykorzystane

### 11.2 Timeline Estimate

**Optimistic:** 16 sesji × 1h = 16 godzin
**Realistic:** 20 sesji × 1.5h = 30 godzin
**Pessimistic:** 25 sesji × 2h = 50 godzin

**Target:** 3-4 tygodnie przy 3-4 sesjach/tydzień

### 11.3 Risk Mitigation

**Potencjalne Problemy & Rozwiązania:**

1. **Gemini API rate limits**
   - Rozwiązanie: Aggressive caching, user warnings

2. **Twitter data brak access**
   - Rozwiązanie: Xscrap cache, manual scraper runs

3. **GPW tickers brak support**
   - Rozwiązanie: Yahoo Finance ma GPW (ticker.WA format)

4. **Streamlit performance z dużymi danymi**
   - Rozwiązanie: Pagination, lazy loading, caching

5. **PDF generation wolny**
   - Rozwiązanie: Async generation, progress bars

### 11.4 Next Session Preparation

**Przed następną sesją:**
1. Zainstaluj Python dependencies (jeśli nie masz)
2. Upewnij się że FRED API key działa
3. Zdobądź Gemini API key (darmowy)
4. Sprawdź czy C:\FRED projekt jest dostępny
5. Przejrzyj ten dokument (STOCKANALYZER_ROADMAP.md)

**W następnej sesji zaczniemy:**
- Faza 1: Foundation & Setup
- Utworzenie struktury katalogów
- Setup bazy danych SQLite
- Podstawowa aplikacja Streamlit

---

## 12. APPENDIX

### 12.1 Useful Resources

**Streamlit:**
- Dokumentacja: https://docs.streamlit.io
- Multi-page: https://docs.streamlit.io/library/get-started/multipage-apps
- Theming: https://docs.streamlit.io/library/advanced-features/theming

**Plotly:**
- Dokumentacja: https://plotly.com/python/
- Cyberpunk theme: Custom templates

**SQLAlchemy:**
- Dokumentacja: https://docs.sqlalchemy.org/
- ORM Tutorial: https://docs.sqlalchemy.org/en/20/orm/tutorial.html

**Gemini API:**
- Dokumentacja: https://ai.google.dev/docs
- Rate limits: https://ai.google.dev/pricing

**ReportLab:**
- Dokumentacja: https://www.reportlab.com/docs/reportlab-userguide.pdf

### 12.2 Example Tickers for Testing

**US Stocks:**
- AAPL (Apple) - tech, large cap
- MSFT (Microsoft) - tech, large cap
- TSLA (Tesla) - tech, volatile
- JPM (JPMorgan) - finance
- XOM (Exxon) - energy

**Polish Stocks (GPW):**
- PKO.WA (PKO Bank Polski)
- CDR.WA (CD Projekt)
- PZU.WA (PZU)
- LPP.WA (LPP)

### 12.3 Contact & Support

**GitHub Repo:** https://github.com/batman-haker/Mega
**Issues:** https://github.com/batman-haker/Mega/issues

---

**KONIEC MASTER ROADMAP**

Data: 2025-11-26
Wersja: 1.0
Status: APPROVED - Ready for Implementation

**Następny krok:** Faza 1 - Foundation & Setup
