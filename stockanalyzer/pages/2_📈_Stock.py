"""
STOCKANALYZER - Stock Analysis Page

Analiza fundamentalna i techniczna pojedynczych akcji.
Wykorzystuje Yahoo Finance + Smart Stock Analyzer.

Features:
- Ticker search
- Smart analysis (0-100 score)
- Fundamentals & Technicals breakdown
- Candlestick charts
- Recommendation: STRONG BUY / BUY / HOLD / SELL / STRONG SELL
"""

import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from datetime import datetime
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from collectors.stock_collector import get_stock_data
from components.cyberpunk_theme import apply_chart_theme
from utils.constants import CHART_COLORS, REGIME_COLORS
from utils.education import (
    get_indicator_help,
    interpret_value,
    SCORING_GLOSSARY,
    FUNDAMENTALS_GLOSSARY,
    TECHNICALS_GLOSSARY
)

# ============================================
# PAGE CONFIG
# ============================================

st.set_page_config(
    page_title="Stock Analysis | STOCKANALYZER",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load cyberpunk theme
from components.cyberpunk_theme import load_cyberpunk_theme
load_cyberpunk_theme()

# ============================================
# HEADER
# ============================================

st.markdown("""
<div style="
    background: linear-gradient(135deg, rgba(26, 26, 46, 0.9), rgba(10, 14, 39, 0.9));
    border: 3px solid #00f5ff;
    border-radius: 12px;
    padding: 2rem;
    text-align: center;
    box-shadow: 0 0 30px #00f5ff80;
    margin-bottom: 2rem;
">
    <h1 style="color: #00f5ff; font-family: 'Orbitron', sans-serif; font-size: 3rem; margin: 0;">
        📈 STOCK ANALYSIS
    </h1>
    <p style="color: #e0e0e0; font-size: 1.2rem; margin: 0.5rem 0 0 0;">
        Analiza fundamentalna i techniczna akcji • Yahoo Finance + Smart Analyzer
    </p>
</div>
""", unsafe_allow_html=True)

# ============================================
# EDUCATIONAL SECTION
# ============================================

with st.expander("📚 PRZEWODNIK DLA POCZĄTKUJĄCYCH - Jak czytać wskaźniki?"):
    st.markdown("""
    ### 🎯 Jak działa Smart Analyzer?

    Analizujemy akcje w **5 kategoriach** i łączymy w **Overall Score (0-100)**:

    1. **Valuation (25%)** - Czy akcja jest tania czy droga?
       - P/E Ratio, P/B Ratio, PEG - porównujemy do sektora
       - **Wyższy score = tańsza akcja**

    2. **Financial Health (20%)** - Jak zdrowa jest firma?
       - ROE, marże, zadłużenie, płynność
       - **Wyższy score = silniejsza firma**

    3. **Growth (25%)** - Jak szybko rośnie?
       - Wzrost przychodów i zysków
       - **Wyższy score = szybszy wzrost**

    4. **Momentum (15%)** - Jaki jest trend cenowy?
       - RSI, MA, pozycja techniczna
       - **Wyższy score = silniejszy trend wzrostowy**

    5. **Sentiment (15%)** - Co myślą analitycy?
       - Rekomendacje i target price
       - **Wyższy score = bardziej pozytywne rekomendacje**

    ---

    ### 📊 Jak interpretować Overall Score?

    - **75-100** 🌟 **EXCELLENT** - Strong buy candidate
    - **60-75** 🟢 **GOOD** - Warta rozważenia
    - **40-60** 🟡 **FAIR** - Neutralna, potrzeba więcej analizy
    - **0-40** 🔴 **POOR** - Unikaj lub sprzedawaj

    ---

    ### 💡 Najważniejsze wskaźniki dla początkujących:

    **Fundamentals:**
    - **P/E Ratio** - Ile płacisz za $1 zysku? Niższe = tańsze
    - **ROE** - Zwrot z kapitału. >15% = dobre, >20% = świetne
    - **Debt/Equity** - Zadłużenie. <1 = bezpieczne, >2 = ryzykowne
    - **Profit Margin** - Ile zostaje zysku? >10% = dobre

    **Technicals:**
    - **RSI** - <30 = oversold (kupuj?), >70 = overbought (sprzedaj?)
    - **MACD** - Histogram > 0 = bullish, < 0 = bearish
    - **MA 50/200** - Golden Cross (MA50 > MA200) = bardzo bullish!

    💡 **Wskazówka:** Najedź na każdą metrykę, aby zobaczyć szczegółowe wyjaśnienie!
    """)

# ============================================
# TICKER INPUT
# ============================================

st.markdown("### 🔍 Wyszukaj Akcję")

# Popular tickers database
POPULAR_TICKERS = {
    "🇺🇸 Tech Giants": ["AAPL - Apple", "MSFT - Microsoft", "GOOGL - Alphabet (Google)",
                         "AMZN - Amazon", "META - Meta (Facebook)", "NVDA - NVIDIA",
                         "TSLA - Tesla", "AMD - AMD"],
    "🇺🇸 Finance": ["JPM - JP Morgan", "BAC - Bank of America", "V - Visa",
                     "MA - Mastercard", "GS - Goldman Sachs"],
    "🇺🇸 Healthcare": ["JNJ - Johnson & Johnson", "UNH - UnitedHealth", "PFE - Pfizer",
                        "ABBV - AbbVie", "TMO - Thermo Fisher"],
    "🇺🇸 Consumer": ["WMT - Walmart", "PG - Procter & Gamble", "KO - Coca-Cola",
                      "PEP - PepsiCo", "NKE - Nike", "MCD - McDonald's"],
    "🇺🇸 Energy": ["XOM - Exxon Mobil", "CVX - Chevron", "COP - ConocoPhillips"],
    "🇵🇱 GPW (Warsaw)": ["PKO.WA - PKO BP", "CDR.WA - CD Projekt", "PKN.WA - PKN Orlen",
                          "PZU.WA - PZU", "ALE.WA - Allegro"],
    "💰 Crypto": ["BTC-USD - Bitcoin", "ETH-USD - Ethereum"],
    "🔧 Własny ticker": ["CUSTOM"]
}

col_input1, col_input2, col_input3 = st.columns([3, 2, 1])

with col_input1:
    # Create flat list for selectbox
    ticker_options = []
    for category, tickers in POPULAR_TICKERS.items():
        ticker_options.append(f"--- {category} ---")
        ticker_options.extend(tickers)

    selected_option = st.selectbox(
        "Wybierz ticker z listy lub wpisz własny",
        options=ticker_options,
        index=ticker_options.index("AAPL - Apple"),
        help="🔍 Zacznij wpisywać aby szybko znaleźć ticker"
    )

    # Parse selected option
    if selected_option.startswith("---"):
        ticker_input = "AAPL"  # Default if header selected
    elif selected_option == "CUSTOM":
        # Show text input for custom ticker
        ticker_input = st.text_input(
            "Wpisz własny ticker:",
            value="",
            placeholder="np. TSLA, NVDA, PKO.WA",
            help="Wpisz dowolny symbol z Yahoo Finance"
        ).upper()
    else:
        # Extract ticker from "TICKER - Name" format
        ticker_input = selected_option.split(" - ")[0].strip().upper()

with col_input2:
    period_select = st.selectbox(
        "Okres Historyczny",
        options=["3mo", "1mo", "6mo", "1y", "2y", "5y"],
        index=0,
        help="Okres dla wykresów i analizy technicznej"
    )

with col_input3:
    analyze_button = st.button(
        "🚀 ANALIZUJ",
        use_container_width=True,
        type="primary"
    )

# ============================================
# ANALYSIS EXECUTION
# ============================================

if ticker_input and (analyze_button or 'stock_data' not in st.session_state or st.session_state.get('last_ticker') != ticker_input):

    # Validate ticker input
    if not ticker_input.strip():
        st.warning("⚠️ Proszę wpisać symbol tickera")
        st.stop()

    if len(ticker_input) > 10:
        st.warning("⚠️ Ticker zbyt długi. Przykłady: AAPL, MSFT, GOOGL, PKO.WA")
        st.stop()

    # Loading progress
    progress_placeholder = st.empty()
    status_placeholder = st.empty()

    try:
        # Stage 1: Fetch data
        progress_placeholder.progress(0.3)
        status_placeholder.info("🔍 Pobieranie danych z Yahoo Finance...")

        stock_data = get_stock_data(ticker_input, period=period_select)

        # Stage 2: Analysis complete
        progress_placeholder.progress(1.0)
        status_placeholder.success("✅ Dane załadowane pomyślnie!")

        # Save to session state
        st.session_state['stock_data'] = stock_data
        st.session_state['last_ticker'] = ticker_input
        st.session_state['load_error'] = None

        # Clear loading indicators
        import time
        time.sleep(0.5)
        progress_placeholder.empty()
        status_placeholder.empty()

    except ValueError as e:
        # Invalid ticker or no data
        progress_placeholder.empty()
        status_placeholder.empty()
        st.error(f"❌ Błąd: {str(e)}")
        st.info("💡 **Sprawdź ticker:**\n- US stocks: AAPL, MSFT, GOOGL, TSLA\n- GPW: PKO.WA, CDR.WA, PKN.WA\n- Crypto: BTC-USD, ETH-USD")
        st.session_state['load_error'] = str(e)
        st.stop()

    except ConnectionError as e:
        # Network issue
        progress_placeholder.empty()
        status_placeholder.empty()
        st.error("❌ Błąd połączenia z Yahoo Finance")
        st.warning("⚠️ Sprawdź połączenie internetowe lub spróbuj ponownie za chwilę")
        st.session_state['load_error'] = "connection_error"
        st.stop()

    except Exception as e:
        # Unknown error
        progress_placeholder.empty()
        status_placeholder.empty()
        error_msg = str(e)

        # Friendly error messages
        if "possibly delisted" in error_msg.lower():
            st.error("❌ Ten ticker może być wycofany z giełdy lub zawieszone notowania")
            st.info("💡 Sprawdź czy symbol jest aktualny")
        elif "no data found" in error_msg.lower():
            st.error("❌ Brak danych dla tego tickera")
            st.info("💡 Sprawdź czy ticker jest poprawny. Przykłady: AAPL, MSFT, GOOGL, PKO.WA")
        elif "404" in error_msg:
            st.error("❌ Ticker nie został znaleziony")
            st.info("💡 Sprawdź czy symbol jest poprawny")
        else:
            st.error(f"❌ Nieoczekiwany błąd: {error_msg}")
            st.info("💡 Spróbuj ponownie lub wybierz inny ticker")

        st.session_state['load_error'] = error_msg
        st.stop()

# ============================================
# DISPLAY RESULTS
# ============================================

if 'stock_data' in st.session_state:
    data = st.session_state['stock_data']

    st.markdown("---")

    # ============================================
    # COMPANY HEADER
    # ============================================

    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, rgba(26, 26, 46, 0.9), rgba(10, 14, 39, 0.9));
        border: 2px solid #ff006e;
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 2rem;
    ">
        <h2 style="color: #00f5ff; font-family: 'Orbitron', sans-serif; margin: 0;">
            {data['company_name']}
        </h2>
        <p style="color: #a0a0a0; font-size: 1.1rem; margin: 0.5rem 0 0 0;">
            {data['sector']} • {data['industry']}
        </p>
        <p style="color: #606060; font-size: 0.9rem; margin: 0.3rem 0 0 0;">
            Ticker: {data['ticker']} | Updated: {data['last_updated']} {'| <span style="color: #39ff14; font-weight: bold;">⚡ FROM CACHE (TTL: 15min)</span>' if data.get('from_cache', False) else ''}
        </p>
    </div>
    """, unsafe_allow_html=True)

    # ============================================
    # MAIN METRICS ROW
    # ============================================

    mcol1, mcol2, mcol3, mcol4 = st.columns(4)

    with mcol1:
        st.metric(
            "💵 Cena Aktualna",
            f"${data['current_price']:.2f}",
            help=f"Market Cap: ${data['market_cap']/1e9:.1f}B"
        )

    with mcol2:
        # Gauge chart dla overall score
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=data['overall_score'],
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Overall Score", 'font': {'size': 16, 'color': '#00f5ff'}},
            number={'suffix': "/100", 'font': {'size': 32, 'color': '#ffffff'}},
            gauge={
                'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "#00f5ff"},
                'bar': {'color': "#00f5ff"},
                'bgcolor': "rgba(26, 26, 46, 0.5)",
                'borderwidth': 2,
                'bordercolor': "#00f5ff",
                'steps': [
                    {'range': [0, 25], 'color': 'rgba(255, 7, 58, 0.3)'},
                    {'range': [25, 40], 'color': 'rgba(255, 190, 11, 0.3)'},
                    {'range': [40, 60], 'color': 'rgba(160, 160, 160, 0.3)'},
                    {'range': [60, 75], 'color': 'rgba(255, 237, 78, 0.3)'},
                    {'range': [75, 100], 'color': 'rgba(57, 255, 20, 0.3)'}
                ],
                'threshold': {
                    'line': {'color': "#ff006e", 'width': 4},
                    'thickness': 0.75,
                    'value': data['overall_score']
                }
            }
        ))

        fig_gauge.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font={'color': "#ffffff", 'family': "Orbitron"},
            height=200,
            margin=dict(l=20, r=20, t=40, b=20)
        )

        st.plotly_chart(fig_gauge, use_container_width=True)

        # Interpretacja Overall Score
        score = data['overall_score']
        interpretation = interpret_value('overall_score', score, 'scoring')
        st.markdown(f"<p style='text-align: center; color: #a0a0a0; font-size: 0.85rem;'>{interpretation}</p>", unsafe_allow_html=True)

    with mcol3:
        # Recommendation badge
        rec_color_map = {
            "🟢 STRONG BUY": "#39ff14",
            "🟡 BUY": "#ffed4e",
            "⚪ HOLD": "#a0a0a0",
            "🟠 SELL": "#ff9500",
            "🔴 STRONG SELL": "#ff073a"
        }

        rec_color = rec_color_map.get(data['recommendation'], '#a0a0a0')

        st.markdown(f"""
        <div style="
            background: rgba(26, 26, 46, 0.8);
            border: 3px solid {rec_color};
            border-radius: 8px;
            padding: 1.5rem;
            text-align: center;
            box-shadow: 0 0 20px {rec_color}80;
            height: 180px;
            display: flex;
            flex-direction: column;
            justify-content: center;
        ">
            <p style="color: #a0a0a0; font-size: 0.9rem; margin: 0 0 0.5rem 0;">
                RECOMMENDATION
            </p>
            <h2 style="color: {rec_color}; font-family: 'Orbitron', sans-serif; font-size: 1.8rem; margin: 0;">
                {data['recommendation']}
            </h2>
        </div>
        """, unsafe_allow_html=True)

    with mcol4:
        # Category scores breakdown (mini chart)
        categories = ['Valuation', 'Health', 'Growth', 'Momentum', 'Sentiment']
        scores = [
            data['valuation_score'],
            data['financial_health_score'],
            data['growth_score'],
            data['momentum_score'],
            data['sentiment_score']
        ]

        fig_breakdown = go.Figure()

        fig_breakdown.add_trace(go.Scatterpolar(
            r=scores,
            theta=categories,
            fill='toself',
            fillcolor='rgba(0, 245, 255, 0.3)',
            line=dict(color='#00f5ff', width=2),
            name='Scores'
        ))

        fig_breakdown.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 100],
                    gridcolor='rgba(0, 245, 255, 0.2)',
                    tickfont=dict(size=10, color='#a0a0a0')
                ),
                angularaxis=dict(
                    gridcolor='rgba(0, 245, 255, 0.2)',
                    tickfont=dict(size=11, color='#ffffff')
                ),
                bgcolor='rgba(0,0,0,0)'
            ),
            showlegend=False,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            height=200,
            margin=dict(l=40, r=40, t=20, b=20)
        )

        st.plotly_chart(fig_breakdown, use_container_width=True)

    # Category scores details with help
    with st.expander("ℹ️ Co oznaczają poszczególne scores?"):
        st.markdown(f"""
        ### 📊 Szczegółowy Breakdown:

        **1. Valuation Score: {data['valuation_score']:.0f}/100** {interpret_value('valuation_score', data['valuation_score'], 'scoring')}
        - Czy akcja jest tania czy droga względem sektora?
        - Wyższy score = tańsza akcja = lepszy value

        **2. Financial Health Score: {data['financial_health_score']:.0f}/100** {interpret_value('financial_health_score', data['financial_health_score'], 'scoring')}
        - Jak silne są fundamenty finansowe?
        - Wyższy score = zdrowsza firma = mniejsze ryzyko

        **3. Growth Score: {data['growth_score']:.0f}/100** {interpret_value('growth_score', data['growth_score'], 'scoring')}
        - Jak szybko rośnie firma?
        - Wyższy score = szybszy wzrost = większy potencjał

        **4. Momentum Score: {data['momentum_score']:.0f}/100** {interpret_value('momentum_score', data['momentum_score'], 'scoring')}
        - Jaki jest trend cenowy i siła momentum?
        - Wyższy score = silniejszy trend wzrostowy

        **5. Sentiment Score: {data['sentiment_score']:.0f}/100** {interpret_value('sentiment_score', data['sentiment_score'], 'scoring')}
        - Co myślą analitycy? Jakie są rekomendacje?
        - Wyższy score = bardziej pozytywne rekomendacje
        """)

    # ============================================
    # SUMMARY
    # ============================================

    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, rgba(26, 26, 46, 0.7), rgba(10, 14, 39, 0.7));
        border-left: 4px solid #00f5ff;
        border-radius: 8px;
        padding: 1.5rem;
        margin: 2rem 0;
    ">
        <h4 style="color: #00f5ff; font-family: 'Orbitron', sans-serif; margin: 0 0 1rem 0;">
            📝 Executive Summary
        </h4>
        <p style="color: #e0e0e0; font-size: 1.1rem; line-height: 1.6; margin: 0;">
            {data['summary']}
        </p>
    </div>
    """, unsafe_allow_html=True)

    # ============================================
    # MAIN ANALYSIS SECTIONS
    # ============================================

    tab1, tab2, tab3, tab4 = st.tabs(["📊 Analysis Breakdown", "📈 Charts", "📉 Fundamentals & Technicals", "🔍 Details"])

    with tab1:
        # Analysis breakdown - strengths, weaknesses, red flags, catalysts

        col_left, col_right = st.columns(2)

        with col_left:
            st.markdown("#### ✅ Strengths")
            if data['strengths']:
                for strength in data['strengths']:
                    st.success(strength)
            else:
                st.info("Brak wyraźnych strengths")

            st.markdown("#### 🚨 Red Flags")
            if data['red_flags']:
                for flag in data['red_flags']:
                    st.error(flag)
            else:
                st.success("✅ Brak red flags!")

        with col_right:
            st.markdown("#### ⚠️ Weaknesses")
            if data['weaknesses']:
                for weakness in data['weaknesses']:
                    st.warning(weakness)
            else:
                st.info("Brak wyraźnych weaknesses")

            st.markdown("#### 🚀 Catalysts")
            if data['catalysts']:
                for catalyst in data['catalysts']:
                    st.info(catalyst)
            else:
                st.info("Brak zidentyfikowanych catalysts")

        # Sector comparison
        st.markdown("---")
        st.markdown("#### 📊 Porównanie do Sektora")

        if data['sector_comparison']:
            comp_col1, comp_col2, comp_col3 = st.columns(3)

            for idx, (metric, comparison) in enumerate(data['sector_comparison'].items()):
                with [comp_col1, comp_col2, comp_col3][idx % 3]:
                    st.metric(metric, comparison)
        else:
            st.info("Brak danych porównawczych")

    with tab2:
        # Candlestick chart
        st.markdown("### 🕯️ Candlestick Chart")

        if data['history']:
            # Create candlestick
            df_hist = pd.DataFrame(data['history'])
            df_hist['date'] = pd.to_datetime(df_hist['date'])

            fig_candle = make_subplots(
                rows=2, cols=1,
                shared_xaxes=True,
                vertical_spacing=0.03,
                subplot_titles=('Price', 'Volume'),
                row_heights=[0.7, 0.3]
            )

            # Candlestick
            fig_candle.add_trace(
                go.Candlestick(
                    x=df_hist['date'],
                    open=df_hist['open'],
                    high=df_hist['high'],
                    low=df_hist['low'],
                    close=df_hist['close'],
                    name='Price',
                    increasing_line_color='#39ff14',
                    decreasing_line_color='#ff073a'
                ),
                row=1, col=1
            )

            # MA lines (jeśli dostępne)
            tech = data['technicals']
            if tech.get('ma_20'):
                # Symuluj MA20 na wykresie (uproszczone)
                fig_candle.add_trace(
                    go.Scatter(
                        x=df_hist['date'],
                        y=[tech['ma_20']] * len(df_hist),
                        mode='lines',
                        name='MA20',
                        line=dict(color='#ffed4e', width=1, dash='dot')
                    ),
                    row=1, col=1
                )

            # Volume
            colors = ['#39ff14' if row['close'] >= row['open'] else '#ff073a' for _, row in df_hist.iterrows()]

            fig_candle.add_trace(
                go.Bar(
                    x=df_hist['date'],
                    y=df_hist['volume'],
                    name='Volume',
                    marker_color=colors,
                    opacity=0.5
                ),
                row=2, col=1
            )

            # Apply theme
            theme_config = apply_chart_theme()
            theme_config.pop('title', None)
            theme_config.pop('legend', None)

            fig_candle.update_layout(
                **theme_config,
                height=600,
                xaxis_rangeslider_visible=False,
                showlegend=True,
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                )
            )

            fig_candle.update_xaxes(gridcolor='rgba(0, 245, 255, 0.1)')
            fig_candle.update_yaxes(gridcolor='rgba(0, 245, 255, 0.1)')

            st.plotly_chart(fig_candle, use_container_width=True)

        else:
            st.warning("Brak danych historycznych")

        # MACD Chart
        st.markdown("---")
        st.markdown("### 📊 MACD (Moving Average Convergence Divergence)")

        tech = data['technicals']
        macd_data = tech.get('macd')

        if macd_data and data['history']:
            df_hist = pd.DataFrame(data['history'])
            df_hist['date'] = pd.to_datetime(df_hist['date'])

            fig_macd = make_subplots(
                rows=2, cols=1,
                shared_xaxes=True,
                vertical_spacing=0.03,
                subplot_titles=('MACD Line & Signal', 'Histogram'),
                row_heights=[0.6, 0.4]
            )

            # MACD Line
            fig_macd.add_trace(
                go.Scatter(
                    x=df_hist['date'],
                    y=macd_data['macd_line'],
                    mode='lines',
                    name='MACD',
                    line=dict(color='#00f5ff', width=2)
                ),
                row=1, col=1
            )

            # Signal Line
            fig_macd.add_trace(
                go.Scatter(
                    x=df_hist['date'],
                    y=macd_data['signal_line'],
                    mode='lines',
                    name='Signal',
                    line=dict(color='#ff006e', width=2)
                ),
                row=1, col=1
            )

            # Histogram
            colors = ['#39ff14' if h > 0 else '#ff073a' for h in macd_data['histogram']]
            fig_macd.add_trace(
                go.Bar(
                    x=df_hist['date'],
                    y=macd_data['histogram'],
                    name='Histogram',
                    marker_color=colors,
                    opacity=0.6
                ),
                row=2, col=1
            )

            # Apply theme
            theme_config = apply_chart_theme()
            theme_config.pop('title', None)
            theme_config.pop('legend', None)

            fig_macd.update_layout(
                **theme_config,
                height=500,
                showlegend=True,
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                )
            )

            fig_macd.update_xaxes(gridcolor='rgba(0, 245, 255, 0.1)')
            fig_macd.update_yaxes(gridcolor='rgba(0, 245, 255, 0.1)')

            st.plotly_chart(fig_macd, use_container_width=True)

            # MACD metrics with interpretation
            col_macd1, col_macd2, col_macd3 = st.columns(3)
            with col_macd1:
                st.metric("MACD", f"{macd_data['current_macd']:.4f}",
                          help="MACD Line = EMA(12) - EMA(26). Pokazuje momentum.")
            with col_macd2:
                st.metric("Signal", f"{macd_data['current_signal']:.4f}",
                          help="Signal Line = EMA(9) of MACD. MACD > Signal = bullish")
            with col_macd3:
                hist_val = macd_data['current_histogram']
                hist_interp = "🟢 BULLISH - Trend wzrostowy" if hist_val > 0 else "🔴 BEARISH - Trend spadkowy"
                st.metric("Histogram", f"{hist_val:.4f}", delta="Bullish" if hist_val > 0 else "Bearish",
                          help="Histogram = MACD - Signal. >0 = bullish, <0 = bearish")
                st.caption(hist_interp)

        else:
            st.info("Brak wystarczających danych do obliczenia MACD (wymagane: 26 dni)")

        # Bollinger Bands Chart
        st.markdown("---")
        st.markdown("### 📈 Bollinger Bands")

        bb_data = tech.get('bollinger_bands')

        if bb_data and data['history']:
            df_hist = pd.DataFrame(data['history'])
            df_hist['date'] = pd.to_datetime(df_hist['date'])

            fig_bb = go.Figure()

            # Upper Band
            fig_bb.add_trace(
                go.Scatter(
                    x=df_hist['date'],
                    y=bb_data['upper_band'],
                    mode='lines',
                    name='Upper Band',
                    line=dict(color='#ff006e', width=1, dash='dash')
                )
            )

            # Middle Band (SMA)
            fig_bb.add_trace(
                go.Scatter(
                    x=df_hist['date'],
                    y=bb_data['middle_band'],
                    mode='lines',
                    name='SMA (20)',
                    line=dict(color='#ffed4e', width=2)
                )
            )

            # Lower Band
            fig_bb.add_trace(
                go.Scatter(
                    x=df_hist['date'],
                    y=bb_data['lower_band'],
                    mode='lines',
                    name='Lower Band',
                    line=dict(color='#ff006e', width=1, dash='dash'),
                    fill='tonexty',
                    fillcolor='rgba(255, 0, 110, 0.1)'
                )
            )

            # Price (Close)
            fig_bb.add_trace(
                go.Scatter(
                    x=df_hist['date'],
                    y=df_hist['close'],
                    mode='lines',
                    name='Close Price',
                    line=dict(color='#00f5ff', width=2)
                )
            )

            # Apply theme
            theme_config = apply_chart_theme()
            theme_config.pop('title', None)
            theme_config.pop('legend', None)

            fig_bb.update_layout(
                **theme_config,
                height=500,
                showlegend=True,
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                )
            )

            fig_bb.update_xaxes(gridcolor='rgba(0, 245, 255, 0.1)')
            fig_bb.update_yaxes(gridcolor='rgba(0, 245, 255, 0.1)')

            st.plotly_chart(fig_bb, use_container_width=True)

            # Bollinger Bands metrics with interpretation
            col_bb1, col_bb2, col_bb3, col_bb4 = st.columns(4)
            with col_bb1:
                st.metric("Upper Band", f"${bb_data['current_upper']:.2f}",
                          help="SMA + 2σ. Cena powyżej = potencjalne wykupienie")
            with col_bb2:
                st.metric("SMA (20)", f"${bb_data['current_middle']:.2f}",
                          help="20-dniowa średnia krocząca (środek pasma)")
            with col_bb3:
                st.metric("Lower Band", f"${bb_data['current_lower']:.2f}",
                          help="SMA - 2σ. Cena poniżej = potencjalne wyprzedanie")
            with col_bb4:
                bw = bb_data['bandwidth']
                bw_interp = "🟡 SQUEEZE - Spodziewany wybuch zmienności" if bw < 5 else "🟢 NORMAL" if bw < 10 else "🔴 HIGH VOLATILITY"
                st.metric("Bandwidth", f"{bw:.2f}%",
                          help="Szerokość pasma (%). <5% = squeeze, >10% = wysoka zmienność")
                st.caption(bw_interp)

        else:
            st.info("Brak wystarczających danych do obliczenia Bollinger Bands (wymagane: 20 dni)")

    with tab3:
        # Fundamentals & Technicals tables

        col_fund, col_tech = st.columns(2)

        with col_fund:
            st.markdown("#### 💰 Fundamentals")

            fund = data['fundamentals']

            fund_data = []

            # Valuation
            if fund.get('pe_ratio'):
                fund_data.append({"Metric": "P/E Ratio", "Value": f"{fund['pe_ratio']:.2f}"})
            if fund.get('pb_ratio'):
                fund_data.append({"Metric": "P/B Ratio", "Value": f"{fund['pb_ratio']:.2f}"})
            if fund.get('peg_ratio'):
                fund_data.append({"Metric": "PEG Ratio", "Value": f"{fund['peg_ratio']:.2f}"})

            # Profitability
            if fund.get('roe'):
                fund_data.append({"Metric": "ROE", "Value": f"{fund['roe']*100:.1f}%"})
            if fund.get('roa'):
                fund_data.append({"Metric": "ROA", "Value": f"{fund['roa']*100:.1f}%"})
            if fund.get('profit_margin'):
                fund_data.append({"Metric": "Profit Margin", "Value": f"{fund['profit_margin']*100:.1f}%"})

            # Debt
            if fund.get('debt_to_equity'):
                fund_data.append({"Metric": "Debt/Equity", "Value": f"{fund['debt_to_equity']:.2f}"})

            # Growth
            if fund.get('revenue_growth'):
                fund_data.append({"Metric": "Revenue Growth", "Value": f"{fund['revenue_growth']*100:.1f}%"})
            if fund.get('earnings_growth'):
                fund_data.append({"Metric": "Earnings Growth", "Value": f"{fund['earnings_growth']*100:.1f}%"})

            # Dividend
            if fund.get('dividend_yield'):
                fund_data.append({"Metric": "Dividend Yield", "Value": f"{fund['dividend_yield']*100:.2f}%"})

            if fund_data:
                df_fund = pd.DataFrame(fund_data)
                st.dataframe(df_fund, use_container_width=True, hide_index=True)

                # Educational expander for fundamentals
                with st.expander("📖 Co to znaczy? (Fundamentals)"):
                    st.markdown("""
                    **P/E Ratio** - Ile płacisz za $1 zysku?
                    - < 15 = tanie, 15-25 = średnie, > 25 = drogie (zależy od sektora!)

                    **PEG Ratio** - P/E z uwzględnieniem wzrostu
                    - < 1 = niedowartościowana, > 2 = przewartościowana

                    **P/B Ratio** - Cena do wartości księgowej
                    - < 1 = poniżej wartości aktywów, > 3 = droga

                    **ROE** - Zwrot z kapitału (%)
                    - > 15% = dobre, > 20% = świetne!

                    **Debt/Equity** - Stosunek długu do kapitału
                    - < 0.5 = niskie zadłużenie, > 1.5 = wysokie ryzyko

                    **Profit Margin** - Marża zysku netto (%)
                    - > 10% = dobre, > 20% = świetne!

                    **Revenue/Earnings Growth** - Wzrost przychodów/zysków (%)
                    - > 15% = strong growth, > 30% = hypergrowth
                    """)
            else:
                st.info("Brak danych fundamentalnych")

        with col_tech:
            st.markdown("#### 📈 Technicals")

            tech = data['technicals']

            tech_data = []

            # Moving Averages
            if tech.get('ma_20'):
                tech_data.append({"Metric": "MA(20)", "Value": f"${tech['ma_20']:.2f}"})
            if tech.get('ma_50'):
                tech_data.append({"Metric": "MA(50)", "Value": f"${tech['ma_50']:.2f}"})
            if tech.get('ma_200'):
                tech_data.append({"Metric": "MA(200)", "Value": f"${tech['ma_200']:.2f}"})

            # Signals
            if tech.get('cross_signal'):
                tech_data.append({"Metric": "MA Signal", "Value": tech['cross_signal']})

            # RSI
            if tech.get('rsi'):
                tech_data.append({"Metric": "RSI(14)", "Value": f"{tech['rsi']:.1f}"})

            # Volume
            if tech.get('volume_signal'):
                tech_data.append({"Metric": "Volume", "Value": tech['volume_signal']})

            # 52w High/Low
            if tech.get('52w_high'):
                tech_data.append({"Metric": "52w High", "Value": f"${tech['52w_high']:.2f}"})
            if tech.get('52w_low'):
                tech_data.append({"Metric": "52w Low", "Value": f"${tech['52w_low']:.2f}"})

            # Beta
            if tech.get('beta'):
                tech_data.append({"Metric": "Beta", "Value": f"{tech['beta']:.2f}"})

            if tech_data:
                df_tech = pd.DataFrame(tech_data)
                st.dataframe(df_tech, use_container_width=True, hide_index=True)

                # Educational expander for technicals
                with st.expander("📖 Co to znaczy? (Technicals)"):
                    st.markdown("""
                    **MA(20/50/200)** - Moving Averages (średnie kroczące)
                    - Cena > MA = trend wzrostowy, Cena < MA = trend spadkowy
                    - MA50 > MA200 = Golden Cross (bardzo bullish!) 🟢
                    - MA50 < MA200 = Death Cross (bardzo bearish!) 🔴

                    **RSI(14)** - Relative Strength Index
                    - < 30 = OVERSOLD (wyprzedane - sygnał kupna?) 🟢
                    - 30-70 = NEUTRAL (normalna strefa) 🟡
                    - > 70 = OVERBOUGHT (wykupione - sygnał sprzedaży?) 🔴

                    **MACD** - Moving Average Convergence Divergence
                    - Histogram > 0 = bullish (trend wzrostowy) 🟢
                    - Histogram < 0 = bearish (trend spadkowy) 🔴
                    - Przecięcie linii MACD z Signal = sygnał kupna/sprzedaży

                    **Bollinger Bands** - Wstęgi zmienności
                    - Cena przy górnej wstędze = potencjalne wykupienie
                    - Cena przy dolnej wstędze = potencjalne wyprzedanie
                    - Wąskie pasmo = niska zmienność, spodziewany wybuch

                    **Beta** - Zmienność względem rynku
                    - < 1 = mniej zmienne niż rynek (mniejsze ryzyko)
                    - = 1 = tak samo zmienne jak rynek
                    - > 1 = bardziej zmienne niż rynek (większe ryzyko i potencjał)
                    """)
            else:
                st.info("Brak danych technicznych")

    with tab4:
        # Raw data & details
        st.markdown("#### 🔍 Raw Data (Debug)")
        st.json(data)

else:
    # No data yet
    st.info("👆 Wpisz ticker i kliknij **ANALIZUJ** aby rozpocząć")

    # Example tickers
    st.markdown("### 💡 Przykładowe Tickery")

    ex_col1, ex_col2, ex_col3, ex_col4 = st.columns(4)

    examples = [
        ("AAPL", "Apple Inc.", "🍎"),
        ("MSFT", "Microsoft", "💻"),
        ("GOOGL", "Alphabet", "🔍"),
        ("TSLA", "Tesla", "🚗"),
        ("NVDA", "NVIDIA", "🎮"),
        ("JPM", "JPMorgan", "🏦"),
        ("PKO.WA", "PKO BP (GPW)", "🇵🇱"),
        ("CDR.WA", "CD Projekt (GPW)", "🎮")
    ]

    for idx, (ticker, name, emoji) in enumerate(examples):
        with [ex_col1, ex_col2, ex_col3, ex_col4][idx % 4]:
            if st.button(f"{emoji} {ticker}", use_container_width=True):
                st.session_state['example_ticker'] = ticker
                st.rerun()

    # Set example ticker if clicked
    if 'example_ticker' in st.session_state:
        ticker_input = st.session_state['example_ticker']
        del st.session_state['example_ticker']

# ============================================
# FOOTER
# ============================================

st.markdown("---")
st.caption("📊 Powered by Yahoo Finance + Smart Stock Analyzer | Data updated in real-time")
