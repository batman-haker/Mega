# 🤖 MEGABOT - AI Investment Advisor

**AI-powered investment analysis combining macro data, stock fundamentals, and expert sentiment**

MEGABOT integrates three powerful data sources and uses Claude/Gemini AI to provide investment recommendations:
- 📊 **FRED** - Macro liquidity analysis (reserves, VIX, yield curve, SOFR spreads)
- 📈 **Stock Analysis** - Fundamentals & technicals via yfinance
- 🐦 **Twitter Sentiment** - Expert opinions from financial Twitter

---

## 🎯 Features

- **Multi-Source Analysis**: Combines macro, fundamental, technical, and sentiment data
- **AI-Powered**: Uses Claude or Gemini AI for expert-level investment recommendations
- **Modular Architecture**: Leverages existing FRED and OpenBB projects
- **Web Dashboard**: Beautiful Streamlit interface
- **CLI Support**: Command-line analysis for automation
- **Scoring System**: Weighted scoring from all data sources

---

## 📁 Project Structure

```
MEGABOT/
├── megabot.py              # Main orchestrator
├── dashboard.py            # Streamlit web interface
├── requirements.txt        # Python dependencies
├── .env.example            # Configuration template
├── config/
│   └── config.py           # Centralized configuration
├── collectors/
│   └── data_collector.py   # Data collection from all sources
├── analyzers/
│   ├── prompt_builder.py   # AI prompt generator
│   └── ai_advisor.py       # Claude/Gemini integration
├── data/                   # Analysis results (auto-generated)
└── logs/                   # Logs (auto-generated)
```

---

## 🚀 Installation

### 1. Prerequisites

- Python 3.9+
- Existing projects:
  - `C:\FRED` - FRED liquidity monitor
  - `C:\openBB` - OpenBB trading terminal
  - `C:\Xscrap` - Twitter scraper

### 2. Install Dependencies

```bash
cd C:\MEGABOT
pip install -r requirements.txt
```

### 3. Configure API Keys

Copy `.env.example` to `.env`:

```bash
copy .env.example .env
```

Edit `.env` and add your API keys:

```env
# FRED API (Required)
FRED_API_KEY=your_fred_api_key_here

# At least one AI API required:
ANTHROPIC_API_KEY=your_claude_api_key_here
GOOGLE_API_KEY=your_gemini_api_key_here
```

**Get API Keys:**
- FRED: https://fred.stlouisfed.org/docs/api/api_key.html (free)
- Claude: https://console.anthropic.com/ (paid)
- Gemini: https://ai.google.dev/ (free tier available)

### 4. Verify Setup

```bash
python config/config.py
```

Should output: `✅ Configuration validated successfully!`

---

## 💻 Usage

### Option 1: Web Dashboard (Recommended)

```bash
streamlit run dashboard.py
```

Then:
1. Open browser to http://localhost:8501
2. Enter stock ticker (e.g. AAPL)
3. Choose AI provider (Claude or Gemini)
4. Click **Analyze** 🚀

### Option 2: Command Line

**Analyze single stock:**
```bash
python megabot.py AAPL
```

**Analyze multiple stocks:**
```bash
python megabot.py AAPL MSFT GOOGL
```

**Use Gemini instead of Claude:**
```bash
python megabot.py AAPL --provider gemini
```

**Help:**
```bash
python megabot.py --help
```

---

## 📊 How It Works

### 1. Data Collection

**FRED Macro Data** (`collectors/data_collector.py`):
- Bank reserves, TGA, Reverse Repo
- SOFR-IORB spread (repo stress indicator)
- VIX, Yield Curve, NFCI
- M2 Money Supply, Dollar Index
- **Score: -100 to +100**

**Stock Analysis**:
- Fundamentals: P/E, ROE, Debt/Equity, margins
- Technicals: RSI, Moving Averages, Golden/Death Cross
- **Score: -100 to +100**

**Twitter Sentiment** (from Xscrap JSON):
- Recent tweets from Dan Kostecki, T_Smolarek, hedgefundowiec, etc.
- Keyword-based sentiment analysis
- **Score: -100 to +100**

### 2. Prompt Building

`analyzers/prompt_builder.py` creates a comprehensive prompt with:
- Formatted macro data (FRED indicators, regime, alerts)
- Stock fundamentals and technicals
- Twitter sentiment summary
- Structured questions for AI

### 3. AI Analysis

`analyzers/ai_advisor.py` sends prompt to:
- **Claude Sonnet 4.5** (recommended) or
- **Gemini 2.0 Flash** (free alternative)

AI provides:
- Buy/Sell/Hold recommendation
- Confidence score
- Risk analysis
- Price targets
- Bull/Base/Bear scenarios

### 4. Combined Scoring

```python
Combined Score = (
    FRED Score × 40% +
    Stock Score × 35% +
    Twitter Score × 25%
)
```

---

## 🔧 Configuration

Edit `config/config.py` to customize:

### Weights

```python
WEIGHTS = {
    'fred_liquidity': 0.40,   # 40% macro
    'stock_technicals': 0.35,  # 35% stock
    'twitter_sentiment': 0.25, # 25% sentiment
}
```

### Twitter Experts

```python
TWITTER_EXPERTS = [
    'Dan_Kostecki',      # Liquidity expert
    'T_Smolarek',        # Macro
    'hedgefundowiec',    # Hedge fund perspective
    # Add more...
]
```

### AI Provider

```python
DEFAULT_AI_PROVIDER = "claude"  # or "gemini"
CLAUDE_MODEL = "claude-3-5-sonnet-20241022"
GEMINI_MODEL = "gemini-2.0-flash-exp"
```

---

## 📖 Example Output

```
╔══════════════════════════════════════════════════════════════╗
║                    🤖 MEGABOT v1.0                          ║
║          AI-Powered Investment Advisor System                ║
╚══════════════════════════════════════════════════════════════╝

🎯 Analyzing AAPL

📊 STEP 1: Data Collection
──────────────────────────────────────────────────────────────
[FRED] Collecting liquidity indicators...
[FRED] ✅ Score: 45.0 | Regime: RISK_ON

[STOCK] Collecting data for AAPL...
[STOCK] ✅ AAPL: $180.50 | Score: 62.0

[TWITTER] Collecting expert tweets...
[TWITTER] ✅ 23 tweets | 5 experts | Sentiment: 58.0

📝 STEP 2: Building AI Prompt
──────────────────────────────────────────────────────────────
[PROMPT] Generated 4523 character prompt

🤖 STEP 3: Getting AI Recommendation
──────────────────────────────────────────────────────────────
[AI] Sending prompt to claude...
[AI] ✅ Received response (2847 chars)

✅ ANALYSIS COMPLETE!
══════════════════════════════════════════════════════════════

Ticker: AAPL
Time: 2025-01-15T10:30:00

📊 SCORES:
  FRED Liquidity:     45.0/100
  Stock Technicals:   62.0/100
  Twitter Sentiment:  58.0/100
  ───────────────────────────────────
  COMBINED SCORE:     54.2/100

🤖 AI RECOMMENDATION: 🟢 BUY
   Provider: CLAUDE (claude-3-5-sonnet-20241022)

──────────────────────────────────────────────────────────────
📄 FULL AI ANALYSIS:
──────────────────────────────────────────────────────────────

1. CZY KUPOWAĆ AAPL TERAZ?

**Rekomendacja: KUP (7/10)**

Warunki makro są sprzyjające (FRED +45), technicals pozytywne
(golden cross, RSI neutralny), a sentiment ekspertów bullish.
Obecny moment jest dobry do budowania pozycji.

2. UZASADNIENIE

**Argumenty ZA:**
- Płynność Fed sprzyja tech stocks (FRED +45, luźne warunki)
- Golden cross (MA50 > MA200) sygnalizuje trend wzrostowy
- Eksperci bullish na tech przez zakończenie QT

**Argumenty PRZECIW:**
- P/E ratio 28x - stosunkowo wysoka wycena
- VIX nisko (18) - może być za dużo optymizmu
- RSI neutralny (55) - brak mocnego momentum

[... pełna analiza ...]

📁 Full results saved to: C:\MEGABOT\data\analysis_AAPL_20250115_103000.json
```

---

## 🔍 Troubleshooting

### "Configuration validation failed"
- Check that FRED/OpenBB/Xscrap directories exist
- Verify API keys in `.env`
- Run: `python config/config.py`

### "No Twitter data found"
- Run your Twitter scraper first (in C:\Xscrap)
- Check that JSON files exist in `C:\Xscrap\x-financial-analyzer\data\cache\`

### "AI API error"
- Check API key is valid
- Check API credit/quota
- Try alternative provider: `--provider gemini`

### "FRED data collection failed"
- Verify FRED_API_KEY
- Check internet connection
- FRED API has rate limits (120 req/min)

---

## 🎨 Dashboard Features

The Streamlit dashboard (`dashboard.py`) includes:

- **Live Analysis**: Real-time stock analysis with one click
- **Multi-Tab Interface**:
  - AI Analysis (full recommendation)
  - Data Details (all raw data)
  - Charts (visual gauges and bars)
  - Raw JSON (for developers)
- **Recent History**: View past analyses
- **Download Options**: Export results as JSON or Markdown

---

## 🚧 Roadmap

- [ ] Portfolio mode (analyze multiple stocks together)
- [ ] Historical backtesting
- [ ] Email alerts
- [ ] Advanced Twitter NLP (LLM-based sentiment)
- [ ] Integration with broker APIs
- [ ] Mobile app

---

## 📝 License

MIT License - Feel free to use and modify!

---

## 🙏 Credits

Built with:
- [FRED](https://fred.stlouisfed.org/) - Federal Reserve Economic Data
- [yfinance](https://github.com/ranaroussi/yfinance) - Stock data
- [Anthropic Claude](https://www.anthropic.com/) - AI analysis
- [Google Gemini](https://ai.google.dev/) - AI analysis
- [Streamlit](https://streamlit.io/) - Dashboard

Inspired by Dan Kostecki's liquidity analysis framework.

---

## 📧 Contact

Questions? Issues? Feedback?
Open an issue on GitHub or contact the developer.

**Happy investing! 🚀📈**
