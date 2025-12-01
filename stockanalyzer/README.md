# STOCKANALYZER - AI Investment Advisor

🚀 **Profesjonalna aplikacja webowa do kompleksowej analizy akcji z wykorzystaniem AI**

---

## ✅ STATUS: FAZA 1 UKOŃCZONA!

**Foundation & Setup** - Kompletne środowisko gotowe do dalszego rozwoju.

### Co zostało zaimplementowane:

- ✅ Struktura projektu (katalogi, moduły)
- ✅ Requirements.txt (wszystkie dependencies)
- ✅ Environment configuration (.env)
- ✅ Utils/Config (centralna konfiguracja)
- ✅ Database models (SQLAlchemy - 7 tabel)
- ✅ Database connection & initialization
- ✅ Cyberpunk theme (custom CSS)
- ✅ Home.py (landing page)

---

## 🚀 Szybki Start

### 1. Instalacja Dependencies

```bash
cd C:\MEGABOT\stockanalyzer
pip install -r requirements.txt
```

### 2. Konfiguracja API Keys

Plik `.env` jest już skonfigurowany z Twoimi kluczami:
- ✅ `FRED_API_KEY` - gotowy
- ✅ `GOOGLE_API_KEY` - gotowy (Gemini)

### 3. Uruchomienie Aplikacji

```bash
# Z katalogu stockanalyzer:
streamlit run Home.py

# LUB (jeśli streamlit nie jest w PATH):
python -m streamlit run Home.py

# LUB (Python launcher):
py -m streamlit run Home.py
```

Aplikacja uruchomi się pod adresem: **http://localhost:8501**

---

## 📁 Struktura Projektu

```
stockanalyzer/
├── Home.py                    # Landing page (entry point)
│
├── pages/                     # Multi-page app (WKRÓTCE)
│   ├── 1_Makro.py            # Faza 2
│   ├── 2_Stock.py            # Faza 3
│   ├── 3_Twitter.py          # Faza 4
│   └── 4_AI_Analysis.py      # Faza 5
│
├── collectors/                # Data collection (WKRÓTCE)
│   ├── fred_collector.py
│   ├── stock_collector.py
│   └── twitter_collector.py
│
├── services/                  # Business logic (WKRÓTCE)
│   ├── analysis_service.py
│   ├── ai_service.py
│   └── pdf_service.py
│
├── database/                  # ✅ GOTOWE
│   ├── models.py             # SQLAlchemy models (7 tabel)
│   └── db.py                 # Connection & init
│
├── utils/                     # ✅ GOTOWE
│   ├── config.py             # Configuration management
│   ├── validators.py         # Input validation (WKRÓTCE)
│   └── constants.py          # Constants (WKRÓTCE)
│
├── components/                # ✅ GOTOWE
│   ├── cyberpunk_theme.py    # Custom CSS
│   ├── charts.py             # Plotly components (WKRÓTCE)
│   └── metrics.py            # Metric components (WKRÓTCE)
│
├── static/                    # Static assets
│   ├── css/
│   ├── images/
│   └── fonts/
│
├── exports/                   # Generated PDFs
│
├── stockanalyzer.db          # SQLite database (auto-created)
├── requirements.txt          # Python dependencies
├── .env                      # API keys (configured)
└── README.md                 # This file
```

---

## 🗄️ Baza Danych (SQLite)

Aplikacja używa SQLite z **7 tabelami**:

1. **analyses** - Główne analizy AI
2. **fred_cache** - Cache wskaźników FRED (TTL: 1h)
3. **stock_cache** - Cache danych giełdowych (TTL: 15min)
4. **twitter_cache** - Cache sentymentu Twitter (TTL: 30min)
5. **user_preferences** - Ulubione eksperci/tickery
6. **pdf_exports** - Historia eksportów PDF
7. **app_logs** - Logi aplikacji

Baza tworzy się **automatycznie** przy pierwszym uruchomieniu Home.py.

Lokalizacja: `C:\MEGABOT\stockanalyzer\stockanalyzer.db`

---

## 🎨 Cyberpunk Theme

Aplikacja używa **profesjonalnego cyberpunk designu**:

- Dark navy gradient background
- Neon cyan (#00f5ff) + magenta (#ff006e) accents
- Orbitron font dla headers
- Share Tech Mono dla liczb
- Glitch effects i scan-line animations
- **BEZ EMOJI** - tylko profesjonalny wygląd

Theme ładuje się automatycznie w każdej stronie przez:
```python
from components.cyberpunk_theme import load_cyberpunk_theme
load_cyberpunk_theme()
```

---

## ⚙️ Konfiguracja

### Plik .env

```env
# FRED API (Makro data)
FRED_API_KEY=your_fred_api_key_here

# Gemini AI (Google)
GOOGLE_API_KEY=your_google_api_key_here

# App settings
DEFAULT_AI_MODEL=gemini-1.5-flash
LANGUAGE=pl

# Cache TTL (seconds)
FRED_CACHE_TTL=3600
STOCK_CACHE_TTL=900
TWITTER_CACHE_TTL=1800

# External paths
FRED_PROJECT_PATH=C:\FRED
XSCRAP_CACHE_PATH=C:\Xscrap\x-financial-analyzer\data\cache
```

**Get API Keys:**
- FRED: https://fred.stlouisfed.org/docs/api/api_key.html (free)
- Gemini: https://ai.google.dev/ (free tier available)

### Walidacja konfiguracji

```bash
# Test konfiguracji:
cd C:\MEGABOT\stockanalyzer
python utils/config.py
```

Output:
```
============================================================
STOCKANALYZER - Configuration
============================================================
Base Directory: C:\MEGABOT\stockanalyzer
Database: C:\MEGABOT\stockanalyzer\stockanalyzer.db
FRED Project: C:\FRED
Xscrap Cache: C:\Xscrap\x-financial-analyzer\data\cache

AI Model: gemini-1.5-flash
Language: pl

Cache TTL:
  - FRED: 3600s
  - Stock: 900s
  - Twitter: 1800s

Scoring Weights:
  - fred_liquidity: 40.0%
  - stock_analysis: 35.0%
  - twitter_sentiment: 25.0%
============================================================

Validating configuration...
✅ Konfiguracja jest poprawna!
```

---

## 🛣️ Roadmapa (następne kroki)

Zapoznaj się z pełnym planem w: **`../STOCKANALYZER_ROADMAP.md`**

### Faza 2: Makro Page (Następna sesja)
- Collector FRED (integracja z C:\FRED)
- Strona 1_Makro.py
- Wykresy Plotly
- Tabela wskaźników

### Faza 3: Stock Page
- Collector Yahoo Finance
- Autocomplete ticker search
- Fundamentals + Technicals
- Price charts

### Faza 4: Twitter Page
- Collector Twitter (Xscrap cache)
- Keyword sentiment
- LLM sentiment (Gemini)
- Timeline

### Faza 5: AI Analysis Page
- Full analysis orchestrator
- Super-prompt builder
- Gemini AI integration
- Results display

### Faza 6: PDF Export
- ReportLab integration
- Cyberpunk PDF styling
- Download functionality

---

## 🧪 Testing

### Test Database

```bash
cd C:\MEGABOT\stockanalyzer
python database/db.py
```

### Test Config

```bash
python utils/config.py
```

### Test Streamlit App

```bash
streamlit run Home.py
```

Otwórz: http://localhost:8501

---

## 📚 Dokumentacja

- **STOCKANALYZER_ROADMAP.md** - Kompletny plan projektu (50+ stron)
- **database/models.py** - Szczegółowe docstringi dla każdej tabeli
- **utils/config.py** - Wszystkie parametry konfiguracyjne
- **components/cyberpunk_theme.py** - CSS theme documentation

---

## 🔧 Troubleshooting

### Problem: `streamlit: command not found`
**Rozwiązanie:**
```bash
python -m streamlit run Home.py
```

### Problem: `ModuleNotFoundError: No module named 'streamlit'`
**Rozwiązanie:**
```bash
pip install -r requirements.txt
```

### Problem: Błędy konfiguracji przy starcie
**Rozwiązanie:**
```bash
# Sprawdź konfigurację:
python utils/config.py

# Upewnij się że istnieją katalogi:
# - C:\FRED
# - C:\Xscrap\x-financial-analyzer\data\cache
```

### Problem: Database errors
**Rozwiązanie:**
```bash
# Usuń bazę i stwórz nową:
del stockanalyzer.db
python database/db.py
```

---

## 🎓 Edukacyjne Aspekty

Każdy moduł zawiera:
- **Docstringi (EN)** - Dokumentacja funkcji w stylu Google
- **Komentarze (PL)** - Wyjaśnienia dla edukacji
- **Type hints** - Jasne definicje typów
- **Examples** - Przykłady użycia w docstringach

Przykład z `database/models.py`:
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

    Example:
        >>> data = get_stock_data("AAPL")
        >>> print(data['current_price'])
        189.50
    """
```

---

## 📞 Support

Pytania? Problemy? Issues?

**GitHub Repo:** https://github.com/batman-haker/Mega

---

## 🏁 Następna Sesja

**Przygotuj się do Fazy 2: Makro Page**

Co będziemy robić:
1. Napisać `collectors/fred_collector.py`
2. Integracja z C:\FRED projekt
3. Stworzyć `pages/1_Makro.py`
4. Wykresy Plotly z danymi FRED
5. Tabela wskaźników z interpretacją

**Czas trwania:** ~1.5-2h
**Poziom:** Średni (integracja z zewnętrznym projektem)

---

**🎉 Gratulacje! Faza 1 ukończona!**

Aplikacja STOCKANALYZER ma solidne fundamenty i jest gotowa na dalszy rozwój.

---

*Powered by Google Gemini AI | Cyberpunk Design | SQLite Database*
