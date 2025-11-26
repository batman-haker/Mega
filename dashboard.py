#!/usr/bin/env python3
"""
MEGABOT Dashboard
Streamlit interface for AI-powered investment analysis
"""

import streamlit as st
import json
import plotly.graph_objects as go
from datetime import datetime
from pathlib import Path

from megabot import MegaBot
from config.config import Config

# Page config
st.set_page_config(
    page_title="MEGABOT - AI Investment Advisor",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Dark theme CSS
st.markdown("""
<style>
    .main {
        background-color: #0e1117;
    }
    .stMetric {
        background-color: #262730;
        padding: 15px;
        border-radius: 10px;
        border-left: 4px solid #00d4ff;
    }
    h1, h2, h3 {
        color: #00d4ff !important;
    }
</style>
""", unsafe_allow_html=True)

# === TITLE ===
st.markdown("""
# 🤖 MEGABOT
### AI-Powered Investment Advisor System
*Combining Macro Data + Stock Analysis + Expert Sentiment*
""")

st.markdown("---")

# === SIDEBAR ===
st.sidebar.title("⚙️ Configuration")

# AI Provider selection
ai_provider = st.sidebar.radio(
    "AI Provider",
    ["claude", "gemini"],
    help="Which AI to use for analysis"
)

st.sidebar.markdown("---")

# Ticker input
ticker_input = st.sidebar.text_input(
    "Stock Ticker",
    value="AAPL",
    help="Enter ticker symbol (e.g. AAPL, MSFT, TSLA)"
).upper()

# Analyze button
analyze_button = st.sidebar.button(
    "🚀 Analyze",
    type="primary",
    use_container_width=True
)

st.sidebar.markdown("---")
st.sidebar.markdown("### ℹ️ About")
st.sidebar.info("""
**MEGABOT** combines:
- 📊 FRED macro liquidity data
- 📈 Stock fundamentals & technicals
- 🐦 Twitter expert sentiment
- 🤖 AI-powered recommendations

Powered by Claude/Gemini AI
""")

# === MAIN AREA ===

# Initialize session state
if 'analysis_result' not in st.session_state:
    st.session_state.analysis_result = None
if 'analyzing' not in st.session_state:
    st.session_state.analyzing = False

# Analyze if button clicked
if analyze_button:
    st.session_state.analyzing = True

if st.session_state.analyzing:
    with st.spinner(f"🔍 Analyzing {ticker_input}..."):
        try:
            # Initialize MEGABOT
            bot = MegaBot(ai_provider=ai_provider)

            # Run analysis
            result = bot.analyze_stock(ticker_input, save_results=True)

            st.session_state.analysis_result = result
            st.session_state.analyzing = False

        except Exception as e:
            st.error(f"❌ Analysis failed: {e}")
            st.session_state.analyzing = False

# Display results
result = st.session_state.analysis_result

if result:
    # === SUMMARY METRICS ===
    st.markdown("## 📊 Analysis Summary")

    col1, col2, col3, col4, col5 = st.columns(5)

    data = result['data']
    ai = result['ai_recommendation']

    # Combined Score
    with col1:
        combined = result['combined_score']
        combined_color = "🟢" if combined > 40 else "🟡" if combined > -40 else "🔴"
        st.metric(
            "Combined Score",
            f"{combined:.1f}/100",
            help="Weighted average of all signals"
        )
        st.markdown(f"<p style='text-align:center; font-size:2em;'>{combined_color}</p>", unsafe_allow_html=True)

    # FRED Score
    with col2:
        fred_score = data['fred']['score'] if data.get('fred') else None
        if fred_score is not None:
            st.metric(
                "FRED Liquidity",
                f"{fred_score:.1f}/100",
                help="Macro liquidity conditions"
            )
            regime = data['fred'].get('regime', {}).get('regime', 'N/A')
            st.caption(f"Regime: {regime}")

    # Stock Score
    with col3:
        stock_score = data['stock']['score'] if data.get('stock') else None
        if stock_score is not None:
            price = data['stock'].get('price', 0)
            change = data['stock'].get('change_1d', 0)
            st.metric(
                "Stock Score",
                f"{stock_score:.1f}/100",
                delta=f"${price:.2f} ({change:+.2f}%)",
                help="Technical & fundamental analysis"
            )

    # Twitter Sentiment
    with col4:
        twitter_score = data['twitter']['sentiment_score'] if data.get('twitter') else None
        if twitter_score is not None:
            tweets_count = data['twitter'].get('tweets_count', 0)
            st.metric(
                "Twitter Sentiment",
                f"{twitter_score:.1f}/100",
                delta=f"{tweets_count} tweets",
                help="Expert sentiment from Twitter"
            )

    # AI Recommendation
    with col5:
        action = ai.get('action', 'UNKNOWN')
        action_emoji = ai.get('action_emoji', '❓')
        st.markdown(f"### {action_emoji} AI Recommendation")
        st.markdown(f"**{action}**")
        st.caption(f"via {ai['provider'].upper()}")

    st.markdown("---")

    # === TABS ===
    tab1, tab2, tab3, tab4 = st.tabs([
        "🤖 AI Analysis",
        "📊 Data Details",
        "📈 Charts",
        "💾 Raw Data"
    ])

    # TAB 1: AI Analysis
    with tab1:
        st.markdown("## 🤖 AI Expert Analysis")
        st.markdown(ai['recommendation'])

        # Download recommendation
        st.download_button(
            label="📥 Download AI Analysis",
            data=ai['recommendation'],
            file_name=f"megabot_{ticker_input}_{datetime.now().strftime('%Y%m%d')}.md",
            mime="text/markdown"
        )

    # TAB 2: Data Details
    with tab2:
        st.markdown("## 📊 Detailed Data Breakdown")

        # FRED Data
        with st.expander("🏦 FRED Macro Data", expanded=True):
            if data.get('fred'):
                fred = data['fred']

                col_a, col_b = st.columns(2)

                with col_a:
                    st.markdown("### Key Indicators")
                    indicators = fred.get('indicators', {})
                    st.json(indicators)

                with col_b:
                    st.markdown("### Regime & Alerts")
                    st.write(f"**Regime:** {fred.get('regime', {}).get('name', 'N/A')}")
                    st.write(f"**Interpretation:** {fred.get('interpretation', '')}")

                    alerts = fred.get('alerts', [])
                    if alerts:
                        st.markdown("**Alerts:**")
                        for alert in alerts:
                            severity = alert.get('severity', 'info')
                            message = alert.get('message', '')
                            if severity == 'critical':
                                st.error(f"🚨 {message}")
                            else:
                                st.warning(f"⚠️ {message}")

        # Stock Data
        with st.expander("📈 Stock Analysis", expanded=True):
            if data.get('stock'):
                stock = data['stock']

                col_a, col_b = st.columns(2)

                with col_a:
                    st.markdown("### Fundamentals")
                    fundamentals = stock.get('fundamentals', {})
                    for key, value in fundamentals.items():
                        if value is not None:
                            st.write(f"**{key}:** {value}")

                with col_b:
                    st.markdown("### Technicals")
                    technicals = stock.get('technicals', {})
                    for key, value in technicals.items():
                        if value is not None:
                            st.write(f"**{key}:** {value}")

        # Twitter Data
        with st.expander("🐦 Twitter Expert Sentiment", expanded=True):
            if data.get('twitter'):
                twitter = data['twitter']

                st.write(f"**Sentiment Score:** {twitter.get('sentiment_score', 0):.1f}/100")
                st.write(f"**Tweets analyzed:** {twitter.get('tweets_count', 0)}")
                st.write(f"**Experts:** {', '.join(['@' + e for e in twitter.get('experts', [])[:5]])}")

                st.markdown("### Recent Tweets")
                tweets = twitter.get('tweets', [])[:5]
                for i, tweet in enumerate(tweets, 1):
                    author = tweet.get('user', {}).get('username', 'unknown')
                    text = tweet.get('text', '')
                    st.markdown(f"**{i}. @{author}**")
                    st.caption(text[:300])
                    st.markdown("---")

    # TAB 3: Charts
    with tab3:
        st.markdown("## 📈 Visual Analysis")

        # Score Gauge
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=result['combined_score'],
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Combined Score", 'font': {'size': 24}},
            delta={'reference': 0},
            gauge={
                'axis': {'range': [-100, 100]},
                'bar': {'color': "darkblue"},
                'steps': [
                    {'range': [-100, -40], 'color': "red"},
                    {'range': [-40, 0], 'color': "orange"},
                    {'range': [0, 40], 'color': "lightblue"},
                    {'range': [40, 100], 'color': "green"}
                ],
                'threshold': {
                    'line': {'color': "black", 'width': 4},
                    'thickness': 0.75,
                    'value': result['combined_score']
                }
            }
        ))

        fig_gauge.update_layout(height=300)
        st.plotly_chart(fig_gauge, use_container_width=True)

        # Score Breakdown
        if data.get('fred') and data.get('stock') and data.get('twitter'):
            fig_bar = go.Figure(data=[
                go.Bar(
                    x=['FRED', 'Stock', 'Twitter', 'Combined'],
                    y=[
                        data['fred']['score'],
                        data['stock']['score'],
                        data['twitter']['sentiment_score'],
                        result['combined_score']
                    ],
                    marker_color=['#4287f5', '#42f545', '#f5a742', '#f542b3']
                )
            ])

            fig_bar.update_layout(
                title="Score Breakdown",
                yaxis_title="Score (-100 to +100)",
                yaxis_range=[-100, 100],
                template="plotly_dark"
            )

            st.plotly_chart(fig_bar, use_container_width=True)

    # TAB 4: Raw Data
    with tab4:
        st.markdown("## 💾 Raw JSON Data")

        st.json(result)

        # Download button
        st.download_button(
            label="📥 Download Full Analysis (JSON)",
            data=json.dumps(result, indent=2, default=str),
            file_name=f"megabot_{ticker_input}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json"
        )

else:
    # Welcome screen
    st.markdown("""
    ## 👋 Welcome to MEGABOT!

    **How it works:**

    1. 📊 **Collects macro data** from FRED (liquidity, VIX, yield curve, etc.)
    2. 📈 **Analyzes stock** fundamentals and technicals
    3. 🐦 **Reads Twitter sentiment** from expert accounts
    4. 🤖 **AI advisor** (Claude/Gemini) gives BUY/SELL recommendation

    ### Get Started:
    1. Enter a stock ticker in the sidebar (e.g. AAPL)
    2. Choose your AI provider (Claude or Gemini)
    3. Click **🚀 Analyze**

    The AI will combine all data sources and give you a detailed investment recommendation!
    """)

    # Show recent analyses
    st.markdown("---")
    st.markdown("### 📂 Recent Analyses")

    data_files = sorted(Config.DATA_DIR.glob("analysis_*.json"), key=lambda x: x.stat().st_mtime, reverse=True)[:5]

    if data_files:
        for i, file in enumerate(data_files, 1):
            with open(file, 'r') as f:
                analysis = json.load(f)

            ticker = analysis.get('ticker', 'N/A')
            timestamp = analysis.get('timestamp', '')
            combined_score = analysis.get('combined_score', 0)
            action = analysis.get('ai_recommendation', {}).get('action', 'N/A')

            st.markdown(f"**{i}. {ticker}** ({timestamp[:10]}) - Score: {combined_score:.1f} - {action}")

    else:
        st.info("No analyses yet. Run your first analysis above!")


# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray;'>
    <p>MEGABOT v1.0 | Powered by Claude/Gemini AI | Data from FRED, yfinance, Twitter</p>
</div>
""", unsafe_allow_html=True)
