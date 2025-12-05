"""
AI ANALYSIS PAGE - Investment Council

Agreguje dane makro + dane spółki + opinie ekspertów AI
Każdy ekspert analizuje spółkę według swojej filozofii inwestycyjnej
"""

import streamlit as st
import pandas as pd
from datetime import datetime
import time

# Load theme
from components.cyberpunk_theme import load_cyberpunk_theme
from utils.mobile_styles import inject_mobile_css

load_cyberpunk_theme()
inject_mobile_css()

# Import expert engine
from utils.expert_engine import (
    load_profiles,
    get_market_data,
    get_macro_data,
    get_expert_opinion
)


# ============================================
# PAGE CONFIG
# ============================================

st.set_page_config(
    page_title="AI Analysis - STOCKANALYZER",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================
# HEADER
# ============================================

st.markdown("""
<div style='text-align: center; padding: 20px 0;'>
    <h1 style='font-size: 3em; margin: 0; background: linear-gradient(135deg, #00f5ff 0%, #ff006e 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;'>
        🧠 AI INVESTMENT COUNCIL
    </h1>
    <p style='font-size: 1.2em; color: #00f5ff; margin-top: 10px;'>
        Ekspercka analiza spółki przez AI symulujące prawdziwych analityków
    </p>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# ============================================
# EXPLANATION
# ============================================

with st.expander("ℹ️ Jak to działa? (Architektura dwuetapowa)", expanded=False):
    st.markdown("""
    **AI Investment Council** to system wykorzystujący "compressed knowledge" - skondensowaną wiedzę ekspertów.

    **ETAP 1 (Offline):** Profile ekspertów
    - Analizujemy tweety, blogi, artykuły eksperta
    - Tworzymy JSON profile (1000 tokenów zamiast 50,000)
    - Profile zawierają: modele myślowe, logikę decyzyjną, styl komunikacji

    **ETAP 2 (Online - w czasie rzeczywistym):**
    - Pobieramy dane o spółce (Yahoo Finance)
    - Pobieramy dane makro (FRED, VIX, Liquidity)
    - Łączymy: Profil JSON + Dane rynkowe → Gemini Flash → Opinia eksperta

    **Koszt:** ~$0.0003 na zapytanie (zamiast $0.01 gdybyśmy wysyłali surowe tweety)

    **Eksperci:**
    - Daniel Kostecki (Gra Płynności) - Hydraulik rynku, analityk płynności
    - _Więcej ekspertów wkrótce..._
    """)

st.markdown("---")


# ============================================
# TICKER INPUT
# ============================================

st.markdown("### 🔍 Wybierz Spółkę do Analizy")

col_input1, col_input2, col_input3 = st.columns([3, 2, 1])

with col_input1:
    ticker_input = st.text_input(
        "Ticker Symbol",
        value="AMD",
        placeholder="np. AAPL, NVDA, AMD, TSLA",
        help="Wpisz symbol giełdowy spółki do analizy"
    ).upper()

with col_input2:
    # Load available experts
    available_profiles = load_profiles()
    expert_names = [p.get('name', 'Unknown') for p in available_profiles]

    if expert_names:
        selected_experts = st.multiselect(
            "Wybierz Ekspertów",
            options=expert_names,
            default=expert_names,  # All selected by default
            help="Wybierz, których ekspertów chcesz skonsultować"
        )
    else:
        st.warning("⚠️ Brak dostępnych profili ekspertów!")
        st.stop()

with col_input3:
    analyze_button = st.button(
        "🚀 ANALIZUJ",
        use_container_width=True,
        type="primary"
    )

# Ticker suggestions expander
with st.expander("📋 Popularne Tickery - Kliknij aby skopiować", expanded=False):
    st.markdown("""
    **🇺🇸 Tech Giants:**
    `AAPL` Apple | `MSFT` Microsoft | `GOOGL` Alphabet | `AMZN` Amazon | `META` Meta | `NVDA` NVIDIA | `AMD` AMD | `TSLA` Tesla | `NFLX` Netflix | `INTC` Intel

    **💰 Finance:**
    `JPM` JPMorgan | `BAC` Bank of America | `WFC` Wells Fargo | `GS` Goldman Sachs | `V` Visa | `MA` Mastercard

    **🏥 Healthcare:**
    `JNJ` Johnson & Johnson | `UNH` UnitedHealth | `PFE` Pfizer | `ABBV` AbbVie | `LLY` Eli Lilly

    **🛒 Consumer:**
    `KO` Coca-Cola | `PEP` PepsiCo | `WMT` Walmart | `HD` Home Depot | `MCD` McDonald's | `NKE` Nike | `SBUX` Starbucks

    **⚡ Energy:**
    `XOM` Exxon Mobil | `CVX` Chevron | `COP` ConocoPhillips

    **🇵🇱 GPW Warszawa:**
    `PKO.WA` PKO BP | `CDR.WA` CD Projekt | `PKN.WA` PKN Orlen | `PZU.WA` PZU | `ALE.WA` Allegro

    **₿ Crypto:**
    `BTC-USD` Bitcoin | `ETH-USD` Ethereum | `SOL-USD` Solana

    **💎 Commodities:**
    `GC=F` Gold | `SI=F` Silver | `CL=F` Crude Oil
    """)

st.markdown("---")


# ============================================
# ANALYSIS EXECUTION
# ============================================

if ticker_input and analyze_button:

    # Validate ticker
    if not ticker_input.strip():
        st.warning("⚠️ Proszę wpisać symbol tickera")
        st.stop()

    if not selected_experts:
        st.warning("⚠️ Wybierz przynajmniej jednego eksperta")
        st.stop()

    # Filter profiles to selected experts
    selected_profiles = [
        p for p in available_profiles
        if p.get('name') in selected_experts
    ]

    # Progress indicators
    progress_bar = st.progress(0)
    status_text = st.empty()

    try:
        # Stage 1: Fetch market data
        status_text.markdown("📊 **Pobieranie danych rynkowych...**")
        progress_bar.progress(0.2)

        market_data = get_market_data(ticker_input)

        if market_data.get('error'):
            st.error(f"❌ Błąd pobierania danych: {market_data['error']}")

            col1, col2 = st.columns([2, 1])
            with col1:
                st.info("""
                💡 **Rozwiązanie:**
                - **Poczekaj 1-2 minuty** i spróbuj ponownie
                - Yahoo Finance ma restrykcyjne limity API
                - **Dane są cachowane przez 1 godzinę** - kolejne zapytania będą szybkie
                - Jeśli używasz Streamlit Cloud, spróbuj **Clear cache** (menu ⋮)
                - Jeśli problem się powtarza, spróbuj innego tickera
                """)
            with col2:
                st.markdown("""
                **🔧 Clear Cache:**
                1. Kliknij ⋮ (góra-prawo)
                2. "Clear cache"
                3. Odśwież stronę
                """)
            st.stop()

        # Stage 2: Fetch macro data
        status_text.markdown("🌍 **Pobieranie danych makroekonomicznych...**")
        progress_bar.progress(0.4)

        macro_data = get_macro_data()

        # Stage 3: Display market summary
        status_text.markdown("✅ **Dane pobrane! Generowanie analiz...**")
        progress_bar.progress(0.6)

        # ============================================
        # MARKET DATA DISPLAY
        # ============================================

        st.markdown(f"## 📊 Przegląd Rynkowy: **{ticker_input}**")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            price = market_data.get('current_price', 0)
            change = market_data.get('change_percent', 0)
            change_color = "#00ff00" if change >= 0 else "#ff0000"

            st.markdown(f"""
            <div style='text-align: center; padding: 15px; background: rgba(0,245,255,0.05); border-radius: 10px; border: 1px solid #00f5ff;'>
                <div style='font-size: 0.9em; color: #888;'>Cena</div>
                <div style='font-size: 2em; font-weight: bold; color: #00f5ff;'>${price:.2f}</div>
                <div style='font-size: 1em; color: {change_color};'>{change:+.2f}%</div>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            rsi = market_data.get('rsi_14', 0)
            rsi_color = "#ff0000" if rsi > 70 else ("#00ff00" if rsi < 30 else "#ffaa00")
            rsi_label = "OVERBOUGHT" if rsi > 70 else ("OVERSOLD" if rsi < 30 else "NEUTRAL")

            st.markdown(f"""
            <div style='text-align: center; padding: 15px; background: rgba(255,0,110,0.05); border-radius: 10px; border: 1px solid #ff006e;'>
                <div style='font-size: 0.9em; color: #888;'>RSI (14)</div>
                <div style='font-size: 2em; font-weight: bold; color: {rsi_color};'>{rsi:.1f}</div>
                <div style='font-size: 0.8em; color: {rsi_color};'>{rsi_label}</div>
            </div>
            """, unsafe_allow_html=True)

        with col3:
            vix = macro_data.get('vix', 0)
            vix_color = "#ff0000" if vix > 25 else ("#00ff00" if vix < 15 else "#ffaa00")

            st.markdown(f"""
            <div style='text-align: center; padding: 15px; background: rgba(255,170,0,0.05); border-radius: 10px; border: 1px solid #ffaa00;'>
                <div style='font-size: 0.9em; color: #888;'>VIX</div>
                <div style='font-size: 2em; font-weight: bold; color: {vix_color};'>{vix:.1f}</div>
                <div style='font-size: 0.8em; color: #888;'>Volatility</div>
            </div>
            """, unsafe_allow_html=True)

        with col4:
            liq_score = macro_data.get('liquidity_score', 0)
            liq_color = "#00ff00" if liq_score > 50 else ("#ff0000" if liq_score < -50 else "#ffaa00")

            st.markdown(f"""
            <div style='text-align: center; padding: 15px; background: rgba(0,255,0,0.05); border-radius: 10px; border: 1px solid #00ff00;'>
                <div style='font-size: 0.9em; color: #888;'>Liquidity Score</div>
                <div style='font-size: 2em; font-weight: bold; color: {liq_color};'>{liq_score:+d}</div>
                <div style='font-size: 0.8em; color: #888;'>Płynność</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")

        # ============================================
        # EXPERT OPINIONS
        # ============================================

        st.markdown("## 🧠 Rada Inwestycyjna")

        opinions = []

        for idx, profile in enumerate(selected_profiles):
            progress = 0.6 + (0.4 * (idx + 1) / len(selected_profiles))
            progress_bar.progress(progress)
            status_text.markdown(f"🤖 **Konsultacja z: {profile.get('name')}...**")

            opinion = get_expert_opinion(profile, ticker_input, market_data, macro_data)
            opinions.append(opinion)

            time.sleep(0.5)  # Small delay for UX

        # Clear progress indicators
        progress_bar.empty()
        status_text.empty()

        # Display opinions in cards
        for opinion in opinions:
            verdict = opinion.get('verdict', 'CZEKAJ')
            verdict_colors = {
                'KUPUJ': '#00ff00',
                'SPRZEDAJ': '#ff0000',
                'CZEKAJ': '#ffaa00',
                'UNIKAJ': '#ff006e',
                'ERROR': '#666666'
            }
            verdict_color = verdict_colors.get(verdict, '#ffaa00')

            st.markdown(f"""
            <div style='background: rgba(0,245,255,0.03); border-left: 4px solid {verdict_color}; padding: 20px; margin: 20px 0; border-radius: 5px;'>
                <div style='display: flex; align-items: center; margin-bottom: 15px;'>
                    <img src='{opinion.get("avatar", "")}' style='width: 50px; height: 50px; border-radius: 50%; margin-right: 15px;'/>
                    <div>
                        <h3 style='margin: 0; color: #00f5ff;'>{opinion.get('expert_name', 'Unknown')}</h3>
                        <p style='margin: 0; color: #888; font-size: 0.9em;'>{opinion.get('expert_role', '')}</p>
                    </div>
                    <div style='margin-left: auto; text-align: right;'>
                        <div style='font-size: 1.5em; font-weight: bold; color: {verdict_color};'>{verdict}</div>
                    </div>
                </div>
                <div style='color: #ccc; line-height: 1.6; white-space: pre-wrap;'>{opinion.get('opinion', 'Brak opinii')}</div>
                <div style='margin-top: 10px; font-size: 0.8em; color: #666;'>
                    🤖 {opinion.get('model_used', 'Unknown model')} |
                    🕐 {opinion.get('timestamp', 'Unknown time')[:19]}
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")

        # ============================================
        # SUMMARY
        # ============================================

        st.markdown("## 📊 Podsumowanie Głosów")

        verdict_counts = {}
        for op in opinions:
            v = op.get('verdict', 'CZEKAJ')
            verdict_counts[v] = verdict_counts.get(v, 0) + 1

        cols = st.columns(len(verdict_counts))

        for idx, (verdict, count) in enumerate(verdict_counts.items()):
            with cols[idx]:
                color = verdict_colors.get(verdict, '#ffaa00')
                st.markdown(f"""
                <div style='text-align: center; padding: 15px; background: rgba(255,255,255,0.03); border-radius: 10px;'>
                    <div style='font-size: 1.5em; color: {color}; font-weight: bold;'>{verdict}</div>
                    <div style='font-size: 2em; color: {color};'>{count}</div>
                    <div style='font-size: 0.9em; color: #888;'>głos(ów)</div>
                </div>
                """, unsafe_allow_html=True)

        st.success(f"✅ Analiza zakończona! Skonsultowano {len(opinions)} ekspertów.")

    except Exception as e:
        st.error(f"❌ Błąd podczas analizy: {str(e)}")
        import traceback
        st.code(traceback.format_exc())


# ============================================
# FOOTER
# ============================================

st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 20px;'>
    <p>🧠 AI Investment Council powered by Google Gemini 1.5 Flash</p>
    <p style='font-size: 0.8em;'>Opinie ekspertów są generowane przez AI i nie stanowią porady inwestycyjnej.</p>
</div>
""", unsafe_allow_html=True)
