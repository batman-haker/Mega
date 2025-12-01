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
# TICKER INPUT
# ============================================

st.markdown("### 🔍 Wyszukaj Akcję")

col_input1, col_input2, col_input3 = st.columns([3, 2, 1])

with col_input1:
    ticker_input = st.text_input(
        "Ticker Symbol",
        value="AAPL",
        placeholder="np. AAPL, MSFT, GOOGL, PKO.WA",
        help="Wpisz symbol giełdowy (US: AAPL, MSFT | GPW: PKO.WA, CDR.WA)"
    ).upper()

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

    with st.spinner(f"📊 Pobieram dane dla {ticker_input}..."):
        try:
            # Fetch data
            stock_data = get_stock_data(ticker_input, period=period_select)

            # Save to session state
            st.session_state['stock_data'] = stock_data
            st.session_state['last_ticker'] = ticker_input

        except Exception as e:
            st.error(f"❌ Błąd: {str(e)}")
            st.info("💡 Sprawdź czy ticker jest poprawny. Przykłady: AAPL, MSFT, GOOGL, PKO.WA")
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

            # MACD metrics
            col_macd1, col_macd2, col_macd3 = st.columns(3)
            with col_macd1:
                st.metric("MACD", f"{macd_data['current_macd']:.4f}")
            with col_macd2:
                st.metric("Signal", f"{macd_data['current_signal']:.4f}")
            with col_macd3:
                hist_val = macd_data['current_histogram']
                st.metric("Histogram", f"{hist_val:.4f}", delta="Bullish" if hist_val > 0 else "Bearish")

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

            # Bollinger Bands metrics
            col_bb1, col_bb2, col_bb3, col_bb4 = st.columns(4)
            with col_bb1:
                st.metric("Upper Band", f"${bb_data['current_upper']:.2f}")
            with col_bb2:
                st.metric("SMA (20)", f"${bb_data['current_middle']:.2f}")
            with col_bb3:
                st.metric("Lower Band", f"${bb_data['current_lower']:.2f}")
            with col_bb4:
                st.metric("Bandwidth", f"{bb_data['bandwidth']:.2f}%")

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
