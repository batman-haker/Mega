"""
STOCKANALYZER - Home Page (Landing Page)

Główna strona aplikacji STOCKANALYZER:
- Welcome message
- Logo i opis projektu
- Nawigacja do podstron
- Quick stats (ile analiz w DB)
- Cyberpunk theme

Uruchomienie:
    streamlit run Home.py
"""

import streamlit as st
import sys
from pathlib import Path

# Dodaj katalog stockanalyzer do Python path
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

# Import custom modules
from components.cyberpunk_theme import load_cyberpunk_theme
from utils.config import Config
from database.db import init_database, check_database_exists, get_database_stats
from utils.mobile_styles import inject_mobile_css
from utils.navigation import render_top_navigation, render_mobile_menu_hint


# ============================================
# PAGE CONFIG
# ============================================

st.set_page_config(
    page_title="STOCKANALYZER - AI Investment Advisor",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"  # ALWAYS expanded - mobile friendly
)

# Load cyberpunk theme
load_cyberpunk_theme()

# Inject mobile-responsive CSS
inject_mobile_css()


# ============================================
# INITIALIZATION
# ============================================

def initialize_app():
    """
    Inicjalizacja aplikacji przy pierwszym uruchomieniu.
    """
    # Sprawdź czy baza istnieje
    if not check_database_exists():
        with st.spinner("Inicjalizacja bazy danych..."):
            init_database()
            st.success("Baza danych utworzona!")


# Initialize on first run
initialize_app()


# ============================================
# TOP NAVIGATION (Fixed at Top)
# ============================================

render_top_navigation(current_page="Home")


# ============================================
# SIDEBAR
# ============================================

with st.sidebar:
    st.markdown("## 📊 STOCKANALYZER")
    st.markdown("---")

    st.markdown("### Nawigacja")
    st.markdown("""
    **Podstrony aplikacji:**

    1. **📊 Makro** - Analiza makroekonomiczna
    2. **📈 Stock** - Dane giełdowe (fundamentals + technicals)
    3. **🧠 AI Analysis** - Kompleksowa analiza AI
    4. **🎮 Gra** - Historyczny Inwestor (edukacyjna gra!)

    Wybierz stronę z menu bocznego ←
    """)

    st.markdown("---")

    # Database stats
    try:
        stats = get_database_stats()
        st.markdown("### Statystyki DB")
        st.metric("Analizy", stats['analyses'])
        st.metric("Cache FRED", stats['fred_cache'])
        st.metric("Cache Stock", stats['stock_cache'])
        st.metric("Cache Twitter", stats['twitter_cache'])
    except Exception as e:
        st.warning(f"Nie można pobrać statystyk: {e}")

    st.markdown("---")

    # Config validation
    is_valid, errors = Config.validate()
    if is_valid:
        st.success("Konfiguracja OK")
    else:
        st.error("Bledy konfiguracji:")
        for key, error in errors.items():
            st.text(f"- {key}: {error}")


# ============================================
# MAIN CONTENT
# ============================================

# Hero section z glitch effect logo
st.markdown("""
<div style="text-align: center; padding: 2rem 0;">
    <h1 class="glitch-text">STOCKANALYZER</h1>
    <p style="font-size: 1.3rem; color: #00f5ff; font-family: 'Orbitron', sans-serif; letter-spacing: 2px;">
        AI-Powered Investment Advisor
    </p>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# Mobile hint
render_mobile_menu_hint()

# Description
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    st.markdown("""
    ## Co to jest STOCKANALYZER?

    **STOCKANALYZER** to profesjonalna aplikacja webowa do kompleksowej analizy akcji,
    łącząca dane z trzech kluczowych źródeł:

    - **📊 FRED (40%)** - Dane makroekonomiczne i płynność rynku
    - **📈 Yahoo Finance (35%)** - Fundamenty i technikalia spółek
    - **🐦 Twitter (25%)** - Sentiment ekspertów finansowych

    Wszystkie dane są analizowane przez **Google Gemini AI**, który generuje
    profesjonalne rekomendacje inwestycyjne.
    """)

st.markdown("---")

# Features
st.markdown("## 🚀 Główne Funkcje")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("""
    ### 📊 Makro
    **Analiza makroekonomiczna**

    - Wskaźniki FRED
    - Liquidity monitoring
    - Market regime detection
    - Wykresy i tabele
    """)

with col2:
    st.markdown("""
    ### 📈 Stock
    **Analiza spółek**

    - Fundamentals (P/E, ROE, ...)
    - Technicals (MA, RSI, ...)
    - Price charts
    - Autocomplete ticker search
    """)

with col3:
    st.markdown("""
    ### 🧠 AI Analysis
    **Kompleksowa analiza**

    - Multi-source fusion
    - AI rekomendacje (Gemini)
    - Risk analysis
    - Scoring system
    """)

with col4:
    st.markdown("""
    ### 🎮 Gra
    **Historyczny Inwestor**

    - Kryzysy finansowe
    - Wielki Kryzys, DotCom
    - Black Monday, Subprime
    - Edukacja przez zabawę
    """)

st.markdown("---")

# Quick start guide
st.markdown("## 🎯 Szybki Start")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    ### 1. Wybierz podstronę

    Użyj nawigacji w bocznym menu (sidebar) aby przejść do:
    - **Makro** - zobacz aktualną sytuację makroekonomiczną
    - **Stock** - przeanalizuj konkretną spółkę
    - **Twitter** - sprawdź co mówią eksperci
    - **AI Analysis** - uzyskaj pełną rekomendację AI
    """)

with col2:
    st.markdown("""
    ### 2. Wprowadź dane

    W zależności od podstrony:
    - Wybierz **ticker** (np. AAPL, MSFT, PKO.WA)
    - Wybierz **eksperta** Twitter (opcjonalnie)
    - Kliknij **"Analizuj"** lub **"Run Analysis"**
    """)

st.markdown("""
### 3. Otrzymaj wynik

Aplikacja:
- Pobierze dane z wszystkich źródeł
- Przetworzy je przez AI (Gemini)
- Wyświetli rekomendację (BUY/HOLD/SELL)
- Pokaże szczegółową analizę
- Umożliwi export do PDF
""")

st.markdown("---")

# Technical info
with st.expander("ℹ️ Informacje Techniczne"):
    st.markdown(f"""
    **Wersja:** 1.0.0 (MVP)

    **Tech Stack:**
    - Frontend: Streamlit {st.__version__}
    - Database: SQLite
    - AI: Google Gemini 1.5 Flash
    - Charts: Plotly
    - PDF: ReportLab

    **Konfiguracja:**
    - Base Directory: `{Config.BASE_DIR}`
    - Database: `{Config.DATABASE_PATH}`
    - FRED Project: `{Config.FRED_PROJECT_PATH}`
    - Xscrap Cache: `{Config.XSCRAP_CACHE_PATH}`

    **Cache TTL:**
    - FRED: {Config.FRED_CACHE_TTL}s (1h)
    - Stock: {Config.STOCK_CACHE_TTL}s (15min)
    - Twitter: {Config.TWITTER_CACHE_TTL}s (30min)

    **Scoring Weights:**
    - FRED: {Config.WEIGHTS['fred_liquidity']*100}%
    - Stock: {Config.WEIGHTS['stock_analysis']*100}%
    - Twitter: {Config.WEIGHTS['twitter_sentiment']*100}%
    """)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #606060; font-size: 0.9rem; padding: 2rem 0;">
    <p>STOCKANALYZER © 2025 | Powered by Google Gemini AI</p>
    <p style="font-size: 0.8rem;">
        Disclaimer: To nie jest porada finansowa. Zawsze przeprowadzaj własne badania przed inwestowaniem.
    </p>
</div>
""", unsafe_allow_html=True)


# ============================================
# DEBUG INFO (tylko w development)
# ============================================

if Config.LOG_LEVEL == "DEBUG":
    with st.expander("🔧 DEBUG INFO"):
        st.write("Session State:", st.session_state)
        st.write("Config:", vars(Config))
