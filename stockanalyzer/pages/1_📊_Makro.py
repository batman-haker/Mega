"""
STOCKANALYZER - Makro Analysis Page (Edukacyjna Wersja)

Analiza makroekonomiczna z wyjaśnieniami każdego terminu!
- Tooltips przy skrótach
- Expanders z humorystycznymi wyjaśnieniami
- Więcej wykresów
- Edukacja + zabawa = łatwiej zapamiętać!
"""

import streamlit as st
import sys
from pathlib import Path
import pandas as pd
from datetime import datetime, timedelta

# Add parent directory to path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

# Imports
from components.cyberpunk_theme import load_cyberpunk_theme
from collectors.fred_collector import FredCollector
from collectors.fear_greed_collector import get_fear_greed_index, FearGreedCollector
from components.charts import (
    create_gauge_meter,
    create_indicators_table,
    create_horizontal_bar,
    create_multi_line_chart,
    create_time_series
)
from utils.constants import REGIME_COLORS, REGIME_DESCRIPTIONS, CHART_COLORS
from utils.financial_glossary import get_explanation, get_all_terms


# ============================================
# PAGE CONFIG
# ============================================

st.set_page_config(
    page_title="Makro Analysis - STOCKANALYZER",
    page_icon="📊",
    layout="wide"
)

load_cyberpunk_theme()


# ============================================
# HEADER
# ============================================

st.markdown("# 📊 Analiza Makroekonomiczna")
st.markdown("### *Edycja Edukacyjna - bo finanse nie muszą być nudne!*")
st.markdown("---")


# ============================================
# SIDEBAR - Ustawienia zakresu dat
# ============================================

with st.sidebar:
    st.header("⚙️ Ustawienia")

    days_range = st.selectbox(
        "📅 Zakres historii",
        options=[30, 90, 180, 365, 730],
        index=4,  # Default: 730 dni
        help="Ile dni wstecz pokazać na wykresach"
    )

    st.info(f"Wybrany zakres: **{days_range} dni** (~{days_range//30} miesięcy)")


# ============================================
# DATA LOADING
# ============================================

@st.cache_data(ttl=1)  # 1 sekunda - wymuszamy reload
def load_fred_data(days_back=730):
    try:
        collector = FredCollector()
        data = collector.get_fred_data(days_back=days_back)
        return data, None
    except Exception as e:
        # Clean error message - usun unicode characters dla Windows console
        error_msg = str(e).encode('ascii', 'replace').decode('ascii')
        return None, error_msg


@st.cache_data(ttl=3600)  # Cache for 1 hour (Fear & Greed updates daily)
def load_fear_greed():
    """Pobiera CNN Fear & Greed Index"""
    try:
        data = get_fear_greed_index(use_cnn=True)
        return data, None
    except Exception as e:
        error_msg = str(e).encode('ascii', 'replace').decode('ascii')
        return None, error_msg


with st.spinner(f"Ładowanie danych FRED ({days_range} dni)..."):
    fred_data, error = load_fred_data(days_back=days_range)

if error:
    st.error(f"Błąd pobierania danych FRED: {error}")
    st.info("💡 **Tip:** Sprawdź czy FRED_API_KEY jest poprawny w .env")

    with st.expander("❓ Co to jest FRED API?"):
        st.markdown("""
        **FRED** = Federal Reserve Economic Data

        To darmowa baza danych ekonomicznych od St. Louis Fed.
        Zawiera ponad 800,000 time-series (historyczne dane).

        **Jak zdobyć klucz:**
        1. Idź na: https://fred.stlouisfed.org/
        2. Zarejestruj się (darmowe!)
        3. Wejdź w My Account → API Keys
        4. Skopiuj klucz do .env jako FRED_API_KEY
        """)
    st.stop()

if not fred_data:
    st.warning("Brak danych FRED")
    st.stop()


# ============================================
# REGIME DETECTION
# ============================================

# Extract regime - może być dict (stary cache) lub string
regime_raw = fred_data.get('regime', 'UNKNOWN')
if isinstance(regime_raw, dict):
    regime = regime_raw.get('regime', 'UNKNOWN')
else:
    regime = regime_raw

score = fred_data.get('score', 0)
alerts = fred_data.get('alerts', [])
indicators = fred_data.get('indicators', {})  # DODANE - potrzebne dla Regime History i innych sekcji

regime_color = REGIME_COLORS.get(regime, '#606060')
regime_desc = REGIME_DESCRIPTIONS.get(regime, 'Brak danych')

# Regime interpretacja
regime_emoji_map = {
    'RISK_ON': '🟢',
    'RISK_OFF': '🟡',
    'CRISIS': '🔴',
    'UNKNOWN': '⚪'
}

# Helper function do pobierania wartości wskaźników
def get_indicator_val(name):
    ind = indicators.get(name, {})
    if isinstance(ind, dict):
        return ind.get('current', 0), ind.get('change_pct', 0)
    return ind, 0
regime_emoji = regime_emoji_map.get(regime, '⚪')

st.markdown(f"""
<div style="
    background: linear-gradient(135deg, rgba(26, 26, 46, 0.9), rgba(10, 14, 39, 0.9));
    border: 3px solid {regime_color};
    border-radius: 12px;
    padding: 2rem;
    text-align: center;
    box-shadow: 0 0 30px {regime_color}80;
    margin-bottom: 2rem;
">
    <h2 style="color: {regime_color}; font-family: 'Orbitron', sans-serif; font-size: 2.5rem; margin: 0;">
        {regime_emoji} {regime}
    </h2>
    <p style="color: #e0e0e0; font-size: 1.2rem; margin: 0.5rem 0 0 0;">
        {regime_desc}
    </p>
    <p style="color: {regime_color}; font-family: 'Share Tech Mono', monospace; font-size: 1.5rem; margin: 1rem 0 0 0;">
        Liquidity Score: {score:+.1f} / 100
    </p>
</div>
""", unsafe_allow_html=True)

# Wyjaśnienie regime
with st.expander("❓ Co to jest Market Regime?"):
    st.markdown("""
    **Market Regime** = Stan rynku w danym momencie

    Wyróżniamy 3 główne stany:

    🟢 **RISK_ON** (Zielone światło!)
    - Wysoka płynność w systemie
    - Niski VIX (brak strachu)
    - Banki mają dużo kasy
    - **Co robić:** Można kupować akcje, ryzykowne aktywa

    🟡 **RISK_OFF** (Ostrożnie!)
    - Płynność się obniża
    - VIX rośnie (rynek się boi)
    - Napięcia w repo market
    - **Co robić:** Defensywa, gotówka, obligacje

    🔴 **CRISIS** (PANIKA!)
    - Krytyczne napięcia płynnościowe
    - VIX > 40 (panika totalna)
    - SOFR-IORB spread eksploduje
    - **Co robić:** Uciekać do dolara/złota, minimalizować ryzyko

    **Fun fact:** Regime może się zmienić w ciągu kilku dni! (COVID: RISK_ON → CRISIS w 2 tygodnie)
    """)


# ============================================
# FEAR & GREED INDEX (CNN)
# ============================================

st.markdown("---")
st.markdown("### 😱 CNN Fear & Greed Index")
st.caption("💡 Wskaźnik sentymentu inwestorów na rynku akcji (0-100)")

# Load Fear & Greed data
fg_data, fg_error = load_fear_greed()

if fg_error:
    st.warning(f"⚠️ Nie udało się pobrać Fear & Greed Index: {fg_error}")
    st.info("💡 Sprawdzę ponownie za godzinę (cache TTL: 1h)")
elif fg_data and fg_data.get('score') is not None:
    collector = FearGreedCollector()
    score = fg_data['score']
    rating = fg_data['rating']

    # Get interpretation
    emoji, label, description = collector.interpret_score(score)

    # Color coding based on score
    if score <= 25:
        color = "#ff073a"  # Red - Extreme Fear
    elif score <= 45:
        color = "#ff8c42"  # Orange - Fear
    elif score <= 55:
        color = "#ffed4e"  # Yellow - Neutral
    elif score <= 75:
        color = "#39ff14"  # Green - Greed
    else:
        color = "#00ff00"  # Bright Green - Extreme Greed

    # Display in a styled box
    col_fg1, col_fg2 = st.columns([1, 2])

    with col_fg1:
        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, rgba(26, 26, 46, 0.9), rgba(10, 14, 39, 0.9));
            border: 3px solid {color};
            border-radius: 12px;
            padding: 2rem;
            text-align: center;
            box-shadow: 0 0 30px {color}80;
        ">
            <h1 style="color: {color}; font-family: 'Orbitron', sans-serif; font-size: 4rem; margin: 0;">
                {emoji}
            </h1>
            <p style="color: {color}; font-family: 'Share Tech Mono', monospace; font-size: 2.5rem; margin: 0.5rem 0;">
                {score:.1f}
            </p>
            <p style="color: #e0e0e0; font-size: 1.2rem; margin: 0.5rem 0 0 0;">
                {label}
            </p>
        </div>
        """, unsafe_allow_html=True)

    with col_fg2:
        st.markdown(f"**Interpretacja:**")
        st.markdown(f"{description}")

        # Show previous values if available
        if fg_data.get('previous_score'):
            prev_score = fg_data['previous_score']
            delta = score - prev_score
            delta_emoji = "📈" if delta > 0 else "📉" if delta < 0 else "➡️"
            st.metric(
                "Zmiana (od poprzedniego)",
                f"{score:.1f}",
                f"{delta:+.1f}",
                help="Zmiana od ostatniego pomiaru"
            )

        if fg_data.get('previous_1week'):
            prev_1w = fg_data['previous_1week']
            delta_1w = score - prev_1w
            st.metric(
                "Zmiana (tydzień)",
                f"{score:.1f}",
                f"{delta_1w:+.1f}",
                help="Zmiana względem tygodnia temu"
            )

    # Educational expander
    with st.expander("❓ Co to Fear & Greed Index?"):
        st.markdown("""
        **Fear & Greed Index** = Wskaźnik strachu i chciwości CNN

        📊 **Jak to działa?**
        CNN analizuje **7 różnych wskaźników** rynkowych:
        1. **Market Momentum** (siła wzrostów)
        2. **Stock Price Strength** (ile akcji bije 52-tygodniowe maksima)
        3. **Stock Price Breadth** (volume akcji rosnących vs spadających)
        4. **Put/Call Options** (ile ludzi kupuje opcje put vs call)
        5. **Junk Bond Demand** (popyt na ryzykowne obligacje)
        6. **Market Volatility** (VIX - indeks zmienności)
        7. **Safe Haven Demand** (popyt na bezpieczne aktywa jak złoto)

        🎯 **Interpretacja skali 0-100:**
        - **0-25** = 😱 **EXTREME FEAR** - Możliwa okazja do kupna?
        - **25-45** = 😰 **FEAR** - Inwestorzy ostrożni
        - **45-55** = 😐 **NEUTRAL** - Rynek zrównoważony
        - **55-75** = 😊 **GREED** - Optymizm rośnie
        - **75-100** = 🤑 **EXTREME GREED** - Ryzyko korekty!

        💡 **Jak to wykorzystać?**
        - **Contrarian approach**: Kupuj gdy strach (< 30), sprzedawaj gdy chciwość (> 70)
        - **Trend following**: Wysoki Fear może zapowiadać dalsze spadki (momentum)
        - **Context matters**: Zawsze łącz z analizą fundamentalną i techniczną!

        🔗 **Źródło:** CNN Business Fear & Greed Index
        """)
else:
    st.info("📊 Fear & Greed Index: Brak danych")

st.markdown("---")


# ============================================
# REGIME HISTORY TIMELINE
# ============================================

st.markdown("### 📅 Regime History - Timeline")
st.caption("💡 Jak zmieniał się market regime w czasie")

try:
    from utils.regime_history import calculate_regime_history, get_regime_stats, detect_regime_transitions
    import plotly.graph_objects as go

    # Oblicz historię regime
    regime_history = calculate_regime_history(indicators)

    if not regime_history.empty and len(regime_history) > 1:
        # Statystyki
        stats = get_regime_stats(regime_history)

        # Metryki w kolumnach
        rhcol1, rhcol2, rhcol3, rhcol4 = st.columns(4)

        with rhcol1:
            total_days = stats['total_days']
            st.metric("📊 Dni w historii", f"{total_days}")

        with rhcol2:
            current = stats['current_regime']
            current_emoji = regime_emoji_map.get(current, '⚪')
            st.metric("🎯 Obecny Regime", f"{current_emoji} {current}")

        with rhcol3:
            if stats['last_regime_change']:
                days_ago = (datetime.now() - pd.to_datetime(stats['last_regime_change'])).days
                st.metric("🔄 Ostatnia zmiana", f"{days_ago} dni temu")
            else:
                st.metric("🔄 Ostatnia zmiana", "Brak zmian")

        with rhcol4:
            longest = stats['longest_streak']
            streak_emoji = regime_emoji_map.get(longest['regime'], '⚪')
            st.metric("🏆 Najdłuższy ciąg", f"{longest['days']} dni ({streak_emoji} {longest['regime']})")

        # Wykres Timeline
        st.markdown("#### 📈 Regime Timeline")

        # Przygotuj dane do wykresu
        regime_history['date_dt'] = pd.to_datetime(regime_history['date'])
        regime_history['regime_numeric'] = regime_history['regime'].map({
            'CRISIS': 3,
            'RISK_OFF': 2,
            'RISK_ON': 1,
            'UNKNOWN': 0
        })

        # Stwórz wykres scatter z kolorami
        fig_timeline = go.Figure()

        # Helper function do konwersji hex na rgba
        def hex_to_rgba(hex_color, alpha=0.3):
            """Konwertuje hex (#RRGGBB) na rgba(r,g,b,a)"""
            hex_color = hex_color.lstrip('#')
            r = int(hex_color[0:2], 16)
            g = int(hex_color[2:4], 16)
            b = int(hex_color[4:6], 16)
            return f'rgba({r},{g},{b},{alpha})'

        # Dodaj obszary kolorowe dla każdego regime (jako filled area)
        for regime_name, regime_num in [('RISK_ON', 1), ('RISK_OFF', 2), ('CRISIS', 3)]:
            regime_data = regime_history[regime_history['regime'] == regime_name]

            if not regime_data.empty:
                color = REGIME_COLORS.get(regime_name, '#606060')
                # Konwertuj na rgba z alpha=0.3 dla przezroczystości
                fillcolor = hex_to_rgba(color, alpha=0.3) if color.startswith('#') else color.replace(')', ', 0.3)').replace('rgb', 'rgba')

                fig_timeline.add_trace(go.Scatter(
                    x=regime_data['date_dt'],
                    y=regime_data['regime_numeric'],
                    mode='lines',
                    name=regime_name,
                    line=dict(color=color, width=0),
                    fill='tonexty' if regime_name != 'RISK_ON' else 'tozeroy',
                    fillcolor=fillcolor,
                    hovertemplate=f'<b>{regime_name}</b><br>Data: %{{x|%Y-%m-%d}}<extra></extra>'
                ))

        # Dodaj linię pokazującą faktyczny regime
        fig_timeline.add_trace(go.Scatter(
            x=regime_history['date_dt'],
            y=regime_history['regime_numeric'],
            mode='lines',
            name='Regime Level',
            line=dict(color='#ffffff', width=2),
            hovertemplate='<b>%{text}</b><br>Data: %{x|%Y-%m-%d}<br>Confidence: %{customdata:.0f}%<extra></extra>',
            text=regime_history['regime'],
            customdata=regime_history['confidence']
        ))

        # Layout
        from components.cyberpunk_theme import apply_chart_theme
        theme_config = apply_chart_theme()
        theme_config.pop('title', None)
        theme_config.pop('yaxis', None)
        theme_config.pop('legend', None)

        fig_timeline.update_layout(
            **theme_config,
            title=f"Market Regime Timeline - Ostatnie {days_range} dni",
            xaxis_title="Data",
            yaxis=dict(
                title="Market Regime",
                tickmode='array',
                tickvals=[1, 2, 3],
                ticktext=['RISK_ON', 'RISK_OFF', 'CRISIS'],
                gridcolor='rgba(0, 245, 255, 0.1)',
                range=[0.5, 3.5]
            ),
            height=400,
            hovermode='x unified',
            legend=dict(
                orientation='h',
                yanchor='bottom',
                y=1.02,
                xanchor='right',
                x=1
            )
        )

        st.plotly_chart(fig_timeline, use_container_width=True)

        # Statystyki rozkładu
        st.markdown("#### 📊 Rozkład Regime")

        statcol1, statcol2 = st.columns(2)

        with statcol1:
            # Pie chart - procent czasu w każdym regime
            regime_pcts = stats['regime_percentages']

            fig_pie = go.Figure(data=[go.Pie(
                labels=list(regime_pcts.keys()),
                values=list(regime_pcts.values()),
                marker=dict(
                    colors=[REGIME_COLORS.get(r, '#606060') for r in regime_pcts.keys()]
                ),
                textinfo='label+percent',
                textfont=dict(size=14, family='Share Tech Mono'),
                hovertemplate='<b>%{label}</b><br>%{value:.1f}%<extra></extra>'
            )])

            theme_pie = apply_chart_theme()
            theme_pie.pop('title', None)

            fig_pie.update_layout(
                **theme_pie,
                title="Procent czasu w każdym regime",
                height=300,
                showlegend=True
            )

            st.plotly_chart(fig_pie, use_container_width=True)

        with statcol2:
            # Tabela z liczbami
            st.markdown("**Statystyki szczegółowe:**")

            for regime_name in ['RISK_ON', 'RISK_OFF', 'CRISIS', 'UNKNOWN']:
                if regime_name in stats['regime_counts']:
                    count = stats['regime_counts'][regime_name]
                    pct = stats['regime_percentages'][regime_name]
                    emoji = regime_emoji_map.get(regime_name, '⚪')
                    color_regime = REGIME_COLORS.get(regime_name, '#606060')

                    st.markdown(f"""
                    <div style="padding: 0.5rem; margin: 0.5rem 0; border-left: 4px solid {color_regime};">
                        <span style="font-size: 1.2rem;">{emoji} <b>{regime_name}</b></span><br>
                        <span style="color: #e0e0e0;">{count} dni ({pct:.1f}%)</span>
                    </div>
                    """, unsafe_allow_html=True)

        # Wykryj transition points
        transitions = detect_regime_transitions(regime_history)

        if not transitions.empty:
            with st.expander(f"🔄 Historia Zmian Regime ({len(transitions)} zmian)"):
                st.markdown("**Ostatnie zmiany market regime:**")

                # Pokaż ostatnie 10 zmian
                recent_transitions = transitions.tail(10).sort_values('date', ascending=False)

                for _, trans in recent_transitions.iterrows():
                    date_str = pd.to_datetime(trans['date']).strftime('%Y-%m-%d')
                    from_regime = trans['from_regime']
                    to_regime = trans['to_regime']
                    from_emoji = regime_emoji_map.get(from_regime, '⚪')
                    to_emoji = regime_emoji_map.get(to_regime, '⚪')

                    st.markdown(f"- **{date_str}:** {from_emoji} {from_regime} → {to_emoji} {to_regime}")

        # Edukacyjne wyjaśnienie
        with st.expander("🎓 Jak czytać Regime History?"):
            st.markdown("""
            ## 📅 Regime History Timeline - Przewodnik

            ### 🎯 Co pokazuje ten wykres?

            **Timeline pokazuje jak zmieniał się market regime w czasie.**

            - **Oś Y:** Poziom regime (RISK_ON → RISK_OFF → CRISIS)
            - **Oś X:** Czas (data)
            - **Kolory:** Taki sam jak główny regime box (zielony/żółty/czerwony)

            ### 📊 Jak interpretować?

            **Długie okresy w jednym regime:**
            - 🟢 **RISK_ON przez 3+ miesiące** → Spokojny bull market
            - 🟡 **RISK_OFF przez 2+ miesiące** → Przedłużająca się korekta
            - 🔴 **CRISIS przez tydzień+** → Poważny kryzys (rzadkie!)

            **Częste zmiany (volatile):**
            - Zmiany co kilka dni → Niezdecydowany rynek, brak trendu
            - Może być trudny okres dla tradingu

            **Wzorce do śledzenia:**

            **🚀 Bullish Pattern:**
            - CRISIS → RISK_OFF → RISK_ON (powrót do normalności)
            - Długi okres RISK_ON (trwały wzrost)

            **🐻 Bearish Pattern:**
            - RISK_ON → RISK_OFF → CRISIS (pogarszanie się warunków)
            - Krótkie powroty do RISK_ON (dead cat bounce)

            ### 💡 Praktyczne użycie:

            **1. Kontekst historyczny:**
            - Jeśli teraz RISK_OFF, ale przez ostatnie 6 miesięcy było RISK_ON
            → Może to być tylko korekta, nie bear market

            **2. Długość ciągów:**
            - RISK_ON przez 200+ dni → Statistycznie może być blisko korekty
            - CRISIS przez 30+ dni → Zwykle dobre miejsce na kupowanie (contrarian)

            **3. Transition points:**
            - Zmiana RISK_OFF → RISK_ON = Zielone światło (wejście)
            - Zmiana RISK_ON → RISK_OFF = Żółte światło (ostrożność)
            - Zmiana RISK_OFF → CRISIS = Czerwone światło (wyjście!)

            ### 📚 Przykłady historyczne:

            **COVID (2020):**
            - Luty: RISK_ON (all time highs)
            - Marzec: CRISIS (VIX 80, panika)
            - Kwiecień-Grudzień: Powrót do RISK_ON (FED money printer)

            **2022 Bear Market:**
            - Styczeń-Marzec: RISK_ON → RISK_OFF (FED zaczyna podnosić stopy)
            - Kwiecień-Październik: Długi RISK_OFF (QT, inflacja)
            - Listopad+: Stopniowy powrót do RISK_ON

            ### 🧠 Pro Tip:

            **Śledź procentowy rozkład:**
            - Portfolio: 70% RISK_ON, 25% RISK_OFF, 5% CRISIS
            → Historycznie sprzyjający okres (można być bardziej agresywnym)

            - Portfolio: 30% RISK_ON, 50% RISK_OFF, 20% CRISIS
            → Trudny okres (ostrożność, cash is king)
            """)

    else:
        st.info("Brak wystarczających danych historycznych do obliczenia Regime History. Potrzebne minimum 30 dni danych.")

except Exception as e:
    st.error(f"Błąd obliczania Regime History: {e}")
    import traceback
    st.code(traceback.format_exc())

st.markdown("---")


# ============================================
# CRITICAL ALERTS
# ============================================

if alerts:
    st.markdown("### ⚠ Critical Alerts")
    for i, alert in enumerate(alerts[:5]):
        st.warning(f"**Alert {i+1}:** {alert}")

    with st.expander("❓ Co to są Critical Alerts?"):
        st.markdown("""
        **Critical Alerts** = Ostrzeżenia automatyczne od LiquidityMonitor

        System wykrywa sytuacje które historycznie poprzedzały problemy:
        - SOFR-IORB spread > 20 bps (repo stress!)
        - Rezerwy < $2.8T (ample → scarce transition)
        - Yield curve inwersja (recesja blisko)
        - VIX > 40 (panika)

        **Nie ignoruj tych alertów!** Zwykle coś się dzieje.
        """)

    st.markdown("---")


# ============================================
# KEY METRICS (z wyjaśnieniami!)
# ============================================

st.markdown("### 📈 Kluczowe Wskaźniki")
st.caption("💡 Kliknij na każdy wskaźnik poniżej aby dowiedzieć się więcej!")

# 4 kolumny z wskaźnikami
col1, col2, col3, col4 = st.columns(4)

with col1:
    vix_val, vix_delta = get_indicator_val('vix')
    st.metric(
        "VIX (Strach)",
        f"{vix_val:.2f}" if vix_val else "N/A",
        f"{vix_delta:+.2f}%",
        delta_color="inverse",
        help="Zmiana vs 30 dni temu"
    )

    with st.expander("❓ Co to VIX?"):
        _, short, long, emoji = get_explanation('VIX')
        st.markdown(long)

with col2:
    sofr_val, sofr_delta = get_indicator_val('sofr')
    st.metric(
        "SOFR",
        f"{sofr_val:.2f}%" if sofr_val else "N/A",
        f"{sofr_delta:+.2f}%",
        help="Zmiana vs 30 dni temu"
    )

    with st.expander("❓ Co to SOFR?"):
        _, short, long, emoji = get_explanation('SOFR')
        st.markdown(long)

with col3:
    yc_val, yc_delta = get_indicator_val('yield_curve')
    st.metric(
        "Yield Curve (10Y-2Y)",
        f"{yc_val:.2f}%" if yc_val else "N/A",
        f"{yc_delta:+.2f}%",
        help="Zmiana vs 30 dni temu"
    )

    with st.expander("❓ Co to Yield Curve?"):
        _, short, long, emoji = get_explanation('YIELD_CURVE')
        st.markdown(long)

with col4:
    m2_val, m2_delta = get_indicator_val('m2')
    m2_display = f"{m2_val/1000:.1f}T" if m2_val and m2_val > 1000 else f"{m2_val:.0f}B" if m2_val else "N/A"
    st.metric(
        "M2 Money Supply",
        m2_display,
        f"{m2_delta:+.2f}%",
        help="Zmiana vs 30 dni temu"
    )

    with st.expander("❓ Co to M2?"):
        _, short, long, emoji = get_explanation('M2')
        st.markdown(long)

st.markdown("---")


# ============================================
# INFLACJA, STOPY PROCENTOWE, WZROST (NOWE!)
# ============================================

st.markdown("### 📊 Inflacja, Stopy Procentowe & Wzrost Gospodarczy")
st.caption("💡 Najważniejsze wskaźniki makro wpływające na politykę Fed!")

# 3 tabs: Inflacja | Stopy Procentowe | Wzrost Gospodarczy
tab_infl, tab_rates, tab_growth = st.tabs(["🔥 Inflacja", "💰 Stopy Procentowe", "📈 Wzrost Gospodarczy"])

with tab_infl:
    st.markdown("#### 🔥 Wskaźniki Inflacji")

    col_inf1, col_inf2, col_inf3, col_inf4 = st.columns(4)

    with col_inf1:
        cpi_val, cpi_delta = get_indicator_val('cpi')
        # CPI jest w formacie index, musimy przeliczyć na YoY% (przybliżenie)
        st.metric(
            "CPI (Consumer Price Index)",
            f"{cpi_delta:.1f}%" if cpi_delta else "N/A",
            help="Wskaźnik cen konsumpcyjnych (YoY change)"
        )
        st.caption("🎯 Cel Fed: **2.0%**")

        with st.expander("❓ Co to CPI?"):
            st.markdown("""
            **CPI** = Consumer Price Index - Indeks Cen Konsumpcyjnych

            📊 **Co mierzy?**
            - Średnią zmianę cen koszyka dóbr i usług kupowanych przez gospodarstwa domowe
            - Obejmuje: żywność, energia, mieszkanie, odzież, transport, opieka zdrowotna

            🎯 **Interpretacja:**
            - **< 2%** = Niska inflacja (deflacja?)
            - **~2%** = CEL FED (idealna inflacja!)
            - **> 3%** = Podwyższona inflacja
            - **> 5%** = Wysoka inflacja (Fed zacieśnia politykę!)

            💡 **Why it matters:**
            Fed używa CPI i PCE do monitorowania inflacji. Wysoka inflacja → wyższe stopy procentowe!
            """)

    with col_inf2:
        pce_val, pce_delta = get_indicator_val('pce')
        st.metric(
            "PCE (Personal Consumption)",
            f"{pce_delta:.1f}%" if pce_delta else "N/A",
            help="Preferowany wskaźnik inflacji Fed (YoY)"
        )
        st.caption("🎯 **PREFEROWANY przez Fed!**")

        with st.expander("❓ Co to PCE?"):
            st.markdown("""
            **PCE** = Personal Consumption Expenditures - Wydatki Konsumpcyjne

            📊 **Dlaczego Fed preferuje PCE nad CPI?**
            - Obejmuje **szerszy zakres** dóbr i usług
            - Uwzględnia **substytucję** (gdy chleb drożeje, ludzie kupują ryż)
            - Bardziej **elastyczny** i **precyzyjny**

            🎯 **Interpretacja:**
            - **< 2%** = Niska inflacja
            - **~2%** = CEL FED (mandate!)
            - **> 2.5%** = Fed zaczyna się martwić
            - **> 3%** = Fed zacieśnia politykę

            💡 **Core PCE** (bez żywności i energii) to **#1 wskaźnik** dla Fed!
            """)

    with col_inf3:
        cpi_core_val, cpi_core_delta = get_indicator_val('cpi_core')
        st.metric(
            "Core CPI",
            f"{cpi_core_delta:.1f}%" if cpi_core_delta else "N/A",
            help="CPI bez żywności i energii (stabilniejszy)"
        )
        st.caption("📌 Bez żywności i energii")

        with st.expander("❓ Dlaczego 'Core'?"):
            st.markdown("""
            **Core CPI** = CPI **bez żywności i energii**

            🤔 **Dlaczego wykluczamy żywność i energię?**
            - Są **bardzo zmienne** (pogoda, geopolityka, OPEC)
            - Nie odzwierciedlają **trwałych trendów** inflacyjnych
            - Core CPI pokazuje **bazową presję inflacyjną**

            💡 **Core inflation** jest lepszym wskaźnikiem **długoterminowych trendów**!
            """)

    with col_inf4:
        infl_5y_val, infl_5y_delta = get_indicator_val('inflation_5y')
        st.metric(
            "5Y Breakeven Inflation",
            f"{infl_5y_val:.2f}%" if infl_5y_val else "N/A",
            f"{infl_5y_delta:+.2f}%",
            help="Oczekiwania inflacyjne na 5 lat (z obligacji)"
        )
        st.caption("🔮 **Oczekiwania rynku**")

        with st.expander("❓ Co to Breakeven Inflation?"):
            st.markdown("""
            **5Y Breakeven Inflation** = Oczekiwana inflacja na najbliższe 5 lat

            📊 **Jak to działa?**
            - Różnica między **nominalną** a **realną** rentownością obligacji Treasury
            - Nominal Treasury Yield - TIPS Yield = Expected Inflation

            🎯 **Interpretacja:**
            - **< 1.5%** = Rynek spodziewa się deflacji/niskiej inflacji
            - **~2%** = Oczekiwania zgodne z celem Fed
            - **> 3%** = Rynek spodziewa się wysokiej inflacji

            💡 Jeśli breakeven > actual inflation → rynek spodziewa się wzrostu inflacji!
            """)

with tab_rates:
    st.markdown("#### 💰 Stopy Procentowe")

    col_rate1, col_rate2, col_rate3 = st.columns(3)

    with col_rate1:
        ff_val, ff_delta = get_indicator_val('fed_funds')
        st.metric(
            "Fed Funds Rate",
            f"{ff_val:.2f}%" if ff_val else "N/A",
            f"{ff_delta:+.2f}%",
            help="Efektywna stopa procentowa Fed"
        )
        st.caption("🎯 **Aktualna stopa Fed**")

        with st.expander("❓ Co to Fed Funds Rate?"):
            st.markdown("""
            **Fed Funds Rate** = Główna stopa procentowa Fed

            📊 **Co to jest?**
            - Stopa, po której banki pożyczają sobie nawzajem **overnight**
            - Ustalana przez **FOMC** (Federal Open Market Committee)
            - Najważniejsza zmienna w polityce monetarnej USA!

            🎯 **Jak wpływa na rynek?**
            - **Wyższe stopy** → droższe pożyczki → wolniejszy wzrost → niższe akcje
            - **Niższe stopy** → tańsze pożyczki → szybszy wzrost → wyższe akcje

            💡 Fed zmienia stopy zwykle o **0.25%** (25 basis points) lub **0.50%** (50 bps)
            """)

    with col_rate2:
        t10_val, t10_delta = get_indicator_val('treasury_10y')
        st.metric(
            "10Y Treasury Yield",
            f"{t10_val:.2f}%" if t10_val else "N/A",
            f"{t10_delta:+.2f}%",
            help="Rentowność 10-letnich obligacji USA"
        )
        st.caption("📊 **Benchmark długu**")

        with st.expander("❓ Dlaczego 10Y Treasury?"):
            st.markdown("""
            **10Y Treasury** = Rentowność 10-letnich obligacji skarbowych USA

            📊 **Dlaczego to ważne?**
            - **Benchmark** dla wszystkich długoterminowych stóp procentowych
            - Wpływa na kredyty hipoteczne, kredyty firmowe
            - Odzwierciedla oczekiwania rynku co do przyszłości

            🎯 **Interpretacja:**
            - **< 2%** = Niskie stopy, obawy o wzrost
            - **2-4%** = Normalne warunki
            - **> 5%** = Wysokie stopy, Fed walczy z inflacją

            💡 Gdy 10Y > Fed Funds = rynek spodziewa się wyższych stóp w przyszłości!
            """)

    with col_rate3:
        t2_val, t2_delta = get_indicator_val('treasury_2y')
        st.metric(
            "2Y Treasury Yield",
            f"{t2_val:.2f}%" if t2_val else "N/A",
            f"{t2_delta:+.2f}%",
            help="Rentowność 2-letnich obligacji USA"
        )
        st.caption("📉 **Short-term rates**")

        with st.expander("❓ Yield Curve (10Y-2Y)?"):
            yc = (t10_val - t2_val) if t10_val and t2_val else None
            if yc:
                st.metric("10Y-2Y Spread", f"{yc:.2f}%",
                          delta="INVERTED!" if yc < 0 else "Normal")

            st.markdown("""
            **Yield Curve Inversion** = 2Y > 10Y (krótkoterminowe wyższe niż długoterminowe)

            🚨 **Dlaczego to ważne?**
            - Historycznie **najlepszy predyktor recesji**!
            - Odwrócona krzywa pojawiła się przed każdą recesją od 1960 roku
            - Zwykle recesja następuje **6-18 miesięcy** po inwersji

            🎯 **Co to oznacza?**
            - Rynek spodziewa się, że Fed będzie musiał **obniżyć stopy** w przyszłości
            - Spowolnienie gospodarcze → niższy popyt na kredyty → niższe stopy
            """)

with tab_growth:
    st.markdown("#### 📈 Wskaźniki Wzrostu Gospodarczego")

    col_gdp1, col_gdp2, col_gdp3 = st.columns(3)

    with col_gdp1:
        gdp_val, gdp_delta = get_indicator_val('gdp_real')
        st.metric(
            "Real GDP",
            f"{gdp_delta:.1f}%" if gdp_delta else "N/A",
            help="Realny PKB (adjusted for inflation, YoY)"
        )
        st.caption("📊 **Wzrost gospodarczy USA**")

        with st.expander("❓ Co to GDP?"):
            st.markdown("""
            **GDP** = Gross Domestic Product - Produkt Krajowy Brutto

            📊 **Co mierzy?**
            - **Całkowitą wartość** wszystkich dóbr i usług wyprodukowanych w USA
            - **Real GDP** = adjusted for inflation (prawdziwy wzrost)

            🎯 **Interpretacja:**
            - **< 0%** = **RECESJA** (2 kwartały pod rząd = oficjalna recesja)
            - **0-1%** = Słaby wzrost
            - **2-3%** = Zdrowy, zrównoważony wzrost
            - **> 3%** = Silny wzrost (ale może prowadzić do inflacji!)

            💡 Średnia długoterminowa dla USA: **~2.5%**
            """)

    with col_gdp2:
        st.warning("⚠️ **ISM Manufacturing: DISCONTINUED**")
        st.caption("🏭 Usunięte z FRED w 2016")

        with st.expander("❓ Dlaczego brak danych ISM?"):
            st.markdown("""
            **ISM Manufacturing & Services** - **DISCONTINUED na FRED**

            ⚠️ **Status:**
            W czerwcu 2016 FRED usunął wszystkie 22 serie ISM ze względów licencyjnych.

            📊 **Co to było ISM/PMI?**
            - **ISM Manufacturing** = Indeks Menedżerów Zakupów (PMI) dla przemysłu
            - Ankieta: nowe zamówienia, produkcja, zatrudnienie, dostawy
            - **Magiczna liczba: 50** (>50 = ekspansja, <50 = skurcz)
            - **Leading indicator** - pokazuje trendy przed GDP!

            🔗 **Gdzie znaleźć dane?**
            - [ISM.org](https://www.ismworld.org/) - oficjalne źródło (płatne)
            - [Trading Economics](https://tradingeconomics.com/united-states/business-confidence) - free
            - [S&P Global PMI](https://www.pmi.spglobal.com/) - alternatywne źródło PMI

            💡 **Ostatni odczyt (październik 2025):**
            - Manufacturing PMI: **48.7** (poniżej 50 = skurcz przemysłu)

            📚 **Źródła:**
            - [FRED Notice 2016](https://news.research.stlouisfed.org/2016/06/institute-for-supply-management-data-to-be-removed-from-fred/)
            - [Trading Economics US PMI](https://tradingeconomics.com/united-states/business-confidence)
            """)

    with col_gdp3:
        st.info("💡 **Dodaj ISM przez API**")
        st.caption("🏢 Trading Economics lub ISM.org")

        with st.expander("💻 Jak dodać ISM/PMI?"):
            st.markdown("""
            **Opcje integracji ISM/PMI:**

            ### 1️⃣ Trading Economics API (Recommended)
            ```python
            # Free tier: 300 requests/month
            import tradingeconomics as te
            te.login('YOUR_API_KEY')
            ism_data = te.getIndicatorData(country='United States',
                                           indicator='Business Confidence')
            ```
            - [Zarejestruj się](https://tradingeconomics.com/analytics/api.aspx)
            - Free tier dostępny!

            ### 2️⃣ S&P Global PMI
            - Alternatywne źródło PMI
            - [S&P Global PMI Data](https://www.pmi.spglobal.com/)

            ### 3️⃣ ISM.org (Oficjalne)
            - Paid subscription
            - Najbardziej dokładne dane
            - [ISM Membership](https://www.ismworld.org/)

            💡 Po dodaniu API key, zakomentuj discontinued series w `liquidity_monitor.py`
            i dodaj nowy collector!
            """)

st.markdown("---")


# ============================================
# LIQUIDITY INDICATORS (TGA, Reserves, RRP, Fed Balance)
# ============================================

st.markdown("### 💧 Główne Wskaźniki Płynności")
st.caption("💡 Kluczowe źródła płynności w systemie finansowym")

# 4 kolumny z liquidity metrics
lcol1, lcol2, lcol3, lcol4 = st.columns(4)

with lcol1:
    reserves_val, reserves_delta = get_indicator_val('reserves_alt')
    reserves_display = f"${reserves_val:.0f}B" if reserves_val else "N/A"
    st.metric(
        "🏦 Rezerwy Banków",
        reserves_display,
        f"{reserves_delta:+.2f}%",
        help="Zmiana vs 30 dni temu"
    )

    with st.expander("❓ Co to Rezerwy?"):
        _, short, long, emoji = get_explanation('RESERVES')
        st.markdown(long)

        st.markdown("---")
        st.markdown("**💡 Wpływ na płynność:**")
        if reserves_val:
            if reserves_val > 3000:
                st.success("✅ **AMPLE** (>$3T): Dużo kasy w systemie - płynność wysoka!")
            elif reserves_val > 2800:
                st.warning("⚠️ **SUFFICIENT** ($2.8-3T): Wystarczająco, ale blisko progu")
            else:
                st.error("🚨 **SCARCE** (<$2.8T): Za mało! Napięcia płynnościowe!")

with lcol2:
    tga_val, tga_delta = get_indicator_val('tga')
    tga_display = f"${tga_val:.0f}B" if tga_val else "N/A"
    st.metric(
        "🏛️ TGA (US Treasury)",
        tga_display,
        f"{tga_delta:+.2f}%",
        delta_color="inverse",  # TGA up = bad dla płynności
        help="Zmiana vs 30 dni temu (odwrotna korelacja z płynnością)"
    )

    with st.expander("❓ Co to TGA?"):
        _, short, long, emoji = get_explanation('TGA')
        st.markdown(long)

        st.markdown("---")
        st.markdown("**💡 Wpływ na płynność:**")
        st.markdown("""
        **TGA ROŚNIE** 📈 = Rząd zbiera podatki/nie wydaje
        - Kasa **WYCHODZI** z systemu bankowego
        - Płynność **SPADA** 📉
        - **Bearish** dla akcji/crypto

        **TGA SPADA** 📉 = Rząd wydaje kasę (emerytury, kontrakty)
        - Kasa **WPŁYWA** do systemu bankowego
        - Płynność **ROŚNIE** 📈
        - **Bullish** dla akcji/crypto

        **Przykład:** Debt ceiling kończy się → TGA spada o $500B → mega boost płynności! 🚀
        """)

with lcol3:
    rrp_val, rrp_delta = get_indicator_val('reverse_repo')
    rrp_display = f"${rrp_val:.0f}B" if rrp_val else "N/A"
    st.metric(
        "🅿️ Reverse Repo",
        rrp_display,
        f"{rrp_delta:+.2f}%",
        delta_color="inverse",  # RRP down = good (kasa wraca na rynek)
        help="Zmiana vs 30 dni temu (odwrotna korelacja z płynnością)"
    )

    with st.expander("❓ Co to RRP?"):
        _, short, long, emoji = get_explanation('RRP')
        st.markdown(long)

        st.markdown("---")
        st.markdown("**💡 Wpływ na płynność:**")
        st.markdown("""
        **RRP = Parking dla nadmiaru gotówki**

        **RRP WYSOKI** (>$1T):
        - Dużo kasy "zaparkowanej" u Fedu
        - Pieniądze **NIE PRACUJĄ** na rynku
        - To bufor bezpieczeństwa (dobra rzecz)

        **RRP SPADA** (<$500B):
        - Kasa **WRACA** na rynek!
        - Płynność **ROŚNIE** 📈
        - **Bullish** dla akcji/crypto

        **Peak COVID:** RRP = $2.5T! (ogromny "parkingnie" kasy)
        **Teraz:** RRP spada = płynność wraca do gry 🚀
        """)

with lcol4:
    fed_bal_val, fed_bal_delta = get_indicator_val('fed_balance')
    fed_bal_display = f"${fed_bal_val/1000:.1f}T" if fed_bal_val else "N/A"
    st.metric(
        "🖨️ Bilans Fed",
        fed_bal_display,
        f"{fed_bal_delta:+.2f}%",
        help="Zmiana vs 30 dni temu"
    )

    with st.expander("❓ Co to Bilans Fed?"):
        _, short, long, emoji = get_explanation('FED_BALANCE')
        st.markdown(long)

        st.markdown("---")
        st.markdown("**💡 Wpływ na płynność:**")
        st.markdown("""
        **Bilans Fedu = Money Printer Status**

        **BILANS ROŚNIE** 📈 = **QE (Quantitative Easing)**
        - FED KUPUJE obligacje (drukuje $)
        - Płynność **EKSPLODUJE** 💥
        - **MEGA BULLISH** dla wszystkiego!
        - Korelacja z S&P500: ~0.8

        **BILANS SPADA** 📉 = **QT (Quantitative Tightening)**
        - FED SPRZEDAJE/nie rolluje obligacji
        - Płynność **WYSYCHA** 🔥
        - **BEARISH** dla akcji/crypto

        **Historia:**
        - 2020-2021: +$5T → S&P +60%, BTC $7k→$69k 🚀
        - 2022-2024: -$1.5T → Bear market 🐻
        """)

# Interpretacja połączona (jak działają razem)
with st.expander("🧠 Jak te wskaźniki działają razem? (MUST READ!)"):
    st.markdown("""
    ## 💧 Formuła Płynności Netto (Net Liquidity)

    **Net Liquidity = Fed Balance - TGA - RRP + Rezerwy**

    ### 🎯 Jak to interpretować:

    **Zwiększa płynność (+):**
    - ✅ Bilans Fed rośnie (QE - drukowanie $)
    - ✅ TGA spada (rząd wydaje kasę)
    - ✅ RRP spada (kasa wraca z "parkingu")
    - ✅ Rezerwy rosną (banki mają więcej $)

    **Zmniejsza płynność (-):**
    - ❌ Bilans Fed spada (QT - niszczenie $)
    - ❌ TGA rośnie (rząd zabiera $ podatkami)
    - ❌ RRP rośnie (kasa ucieka do "parkingu")
    - ❌ Rezerwy spadają (banki mają mniej $)

    ---

    ## 📊 Scenariusze Realne:

    ### 🚀 **LIQUIDITY FLOOD** (Best case):
    - Fed Balance ⬆️ (QE!)
    - TGA ⬇️ (rząd wydaje)
    - RRP ⬇️ (kasa wraca)
    - Rezerwy ⬆️ (banki mają kasę)

    **= TURBO PŁYNNOŚĆ! Akcje/crypto TO THE MOON! 🌙**

    ### 🐻 **LIQUIDITY DRAIN** (Worst case):
    - Fed Balance ⬇️ (QT!)
    - TGA ⬆️ (rząd zbiera podatki)
    - RRP ⬆️ (kasa ucieka)
    - Rezerwy ⬇️ (banki kurczą kasę)

    **= PŁYNNOŚĆ WYSYCHA! Wszystko spada! 📉**

    ---

    ## 💡 Dan Kostecki Pro Tip:

    > "Forget fundamentals. Follow the liquidity.
    > Fed Balance + TGA + RRP tells you everything."

    **Translation:**
    Nie ważne jak dobre są zarobki firm.
    Jak płynność spada = wszystko spada.
    Jak płynność rośnie = wszystko rośnie.

    **It's that simple.** 🎯
    """)

st.markdown("---")


# ============================================
# NET LIQUIDITY (Dan Kostecki Formula)
# ============================================

st.markdown("### 💧 NET LIQUIDITY - Główna Metryka Płynności")
st.caption("💡 Formuła Dan Kosteckiego: Fed Balance - TGA - RRP (w miliardach USD)")

try:
    # Pobierz wartości wskaźników
    fed_balance_val, _ = get_indicator_val('fed_balance')
    tga_val, _ = get_indicator_val('tga')
    rrp_val, _ = get_indicator_val('reverse_repo')

    # Oblicz Net Liquidity (w miliardach)
    # Uwaga: fed_balance jest już w B, nie trzeba dzielić
    if all(v is not None for v in [fed_balance_val, tga_val, rrp_val]):
        net_liquidity = fed_balance_val - tga_val - rrp_val

        # Metryki w kolumnach
        nlcol1, nlcol2, nlcol3 = st.columns(3)

        with nlcol1:
            st.metric(
                "💧 Net Liquidity",
                f"${net_liquidity:.0f}B",
                help="Fed Balance - TGA - RRP"
            )

        with nlcol2:
            # Porównanie do poprzedniego miesiąca (uproszczone - użyjemy change z fed_balance jako proxy)
            _, fed_change = get_indicator_val('fed_balance')
            st.metric(
                "Trend (30d)",
                "Wzrost" if fed_change > 0 else "Spadek",
                f"{fed_change:+.1f}%"
            )

        with nlcol3:
            # Interpretacja
            if net_liquidity > 5000:
                status = "🟢 Bardzo Wysoka"
                status_color = "green"
            elif net_liquidity > 4000:
                status = "🟢 Wysoka"
                status_color = "green"
            elif net_liquidity > 3000:
                status = "🟡 Umiarkowana"
                status_color = "orange"
            else:
                status = "🔴 Niska"
                status_color = "red"

            st.metric(
                "Status",
                status
            )

        # Wykres Net Liquidity w czasie
        st.markdown("#### 📈 Net Liquidity - Trend Historyczny")

        # Sprawdź czy mamy dane historyczne
        if ('fed_balance' in indicators and 'data' in indicators['fed_balance'] and
            'tga' in indicators and 'data' in indicators['tga'] and
            'reverse_repo' in indicators and 'data' in indicators['reverse_repo']):

            try:
                # Połącz dane z trzech źródeł
                fed_df = indicators['fed_balance']['data'][['date', 'value']].copy()
                fed_df = fed_df.rename(columns={'value': 'fed_balance'})

                tga_df = indicators['tga']['data'][['date', 'value']].copy()
                tga_df = tga_df.rename(columns={'value': 'tga'})

                rrp_df = indicators['reverse_repo']['data'][['date', 'value']].copy()
                rrp_df = rrp_df.rename(columns={'value': 'rrp'})

                # Merge wszystkich trzech
                net_liq_df = fed_df.merge(tga_df, on='date', how='inner')
                net_liq_df = net_liq_df.merge(rrp_df, on='date', how='inner')

                # Oblicz Net Liquidity
                net_liq_df['Net Liquidity'] = (
                    net_liq_df['fed_balance'] -
                    net_liq_df['tga'] -
                    net_liq_df['rrp']
                )

                # Stwórz wykres
                net_liq_fig = create_time_series(
                    data=net_liq_df,
                    x_column='date',
                    y_column='Net Liquidity',
                    title=f"Net Liquidity - Ostatnie {days_range} dni",
                    y_axis_title="Net Liquidity ($B)",
                    color=CHART_COLORS['line_neutral']
                )

                st.plotly_chart(net_liq_fig, use_container_width=True)

                # Statystyki Net Liquidity
                nlstat1, nlstat2, nlstat3, nlstat4 = st.columns(4)

                with nlstat1:
                    st.metric("Minimum", f"${net_liq_df['Net Liquidity'].min():.0f}B")
                with nlstat2:
                    st.metric("Maksimum", f"${net_liq_df['Net Liquidity'].max():.0f}B")
                with nlstat3:
                    st.metric("Średnia", f"${net_liq_df['Net Liquidity'].mean():.0f}B")
                with nlstat4:
                    current_vs_avg = net_liquidity - net_liq_df['Net Liquidity'].mean()
                    st.metric("vs Średnia", f"{current_vs_avg:+.0f}B")

            except Exception as e:
                st.warning(f"Nie można utworzyć wykresu Net Liquidity: {e}")
        else:
            st.info("Brak danych historycznych dla wykresu Net Liquidity")

        # Edukacyjne wyjaśnienie
        with st.expander("🎓 Co to jest Net Liquidity i czemu jest NAJWAŻNIEJSZA?"):
            st.markdown(f"""
            ## 💧 Net Liquidity = Money Printer Power!

            **Formuła:**
            ```
            Net Liquidity = Fed Balance - TGA - RRP
            ```

            **Obecna wartość: ${net_liquidity:.0f}B**

            ### 📊 Komponenty:
            - **Fed Balance:** ${fed_balance_val:.0f}B (ile FED ma aktywów)
            - **TGA:** ${tga_val:.0f}B (konto rządu - blokuje płynność)
            - **RRP:** ${rrp_val:.0f}B (zaparkowana kasa - nie pracuje)

            ### 🎯 Dlaczego to najważniejsze?

            **Dan Kostecki mówi:**
            > "Net Liquidity to JEDYNY wskaźnik który potrzebujesz.
            > Rośnie = akcje/crypto up. Spada = akcje/crypto down.
            > Forget everything else."

            **Jak to działa:**

            **🚀 Net Liquidity ROŚNIE gdy:**
            - ✅ Fed robi QE (kupuje obligacje) → Fed Balance up
            - ✅ Rząd wydaje kasę → TGA down
            - ✅ Kasa wraca z RRP parkingu → RRP down

            **= Więcej kasy w systemie = Akcje/Crypto UP!**

            **📉 Net Liquidity SPADA gdy:**
            - ❌ Fed robi QT (sprzedaje obligacje) → Fed Balance down
            - ❌ Rząd zbiera podatki → TGA up
            - ❌ Kasa ucieka do RRP → RRP up

            **= Mniej kasy w systemie = Akcje/Crypto DOWN!**

            ### 📈 Korelacja z rynkiem:

            Net Liquidity vs S&P500: **~0.85 korelacja** (2020-2024)

            **Przykłady z historii:**

            **COVID (2020-2021):**
            - Net Liq: +$5T w rok 🚀
            - S&P500: +60%
            - Bitcoin: $7k → $69k

            **QT Era (2022-2024):**
            - Net Liq: -$1.5T 📉
            - S&P500: -20% (bear market)
            - Bitcoin: $69k → $16k

            ### 💡 Jak to używać w tradingu:

            1. **Śledź trend Net Liquidity** (wykres wyżej)
            2. **Net Liq rośnie 3 miesiące z rzędu?** → Czas kupować
            3. **Net Liq spada 3 miesiące z rzędu?** → Czas sprzedawać

            **To nie jest timing tool** (nie przewiduje dokładnie),
            ale pokazuje **kierunek** dokąd płynie płynność.

            **TL;DR:**
            Net Liquidity to paliwowy wskaźnik dla rynku.
            Więcej paliwa = rynek jedzie. Mniej paliwa = rynek stoi.
            """)

    else:
        st.warning("Brak danych do obliczenia Net Liquidity (potrzebne: Fed Balance, TGA, RRP)")

except Exception as e:
    st.error(f"Błąd obliczania Net Liquidity: {e}")

st.markdown("---")


# ============================================
# SCORE BREAKDOWN
# ============================================

st.markdown("### 🎯 Analiza Score")

col_gauge, col_bar = st.columns(2)

with col_gauge:
    gauge_fig = create_gauge_meter(
        value=score,
        title="Overall Liquidity Score"
    )
    st.plotly_chart(gauge_fig, use_container_width=True)

    with st.expander("❓ Jak interpretować Score?"):
        st.markdown("""
        **Liquidity Score** = Ocena ogólnych warunków płynnościowych (-100 do +100)

        **Skala:**
        - **+70 do +100:** SUPER BULL! Wszystko super, płynność wysoka
        - **+30 do +70:** Dobrze, zielone światło dla akcji
        - **-30 do +30:** Neutralnie, tak sobie
        - **-70 do -30:** Słabo, ostrożność wskazana
        - **-100 do -70:** KATASTROFA! Ucieka kto może!

        **Składa się z:**
        - Wskaźniki płynności (SOFR, rezerwy, RRP)
        - Wskaźniki ryzyka (VIX, HY spread)
        - Warunki finansowe (NFCI, yield curve)

        Ważone według systemu Dan Kosteckiego (liquidity expert).
        """)

with col_bar:
    # Rozłożenie score na komponenty (uproszczone dla MVP)
    component_scores = {
        'Liquidity': score * 0.4,
        'Risk Sentiment': score * 0.3,
        'Conditions': score * 0.3
    }

    bar_fig = create_horizontal_bar(
        labels=list(component_scores.keys()),
        values=list(component_scores.values()),
        title="Score Components"
    )
    st.plotly_chart(bar_fig, use_container_width=True)

st.markdown("---")


# ============================================
# DETAILED INDICATORS TABLE
# ============================================

st.markdown("### 📋 Wszystkie Wskaźniki (Szczegółowo)")

try:
    collector = FredCollector()
    summary = collector.get_key_indicators_summary()

    if summary:
        # Dodaj expander dla każdego wskaźnika w tabeli
        table_df = create_indicators_table(summary)
        st.dataframe(
            table_df,
            use_container_width=True,
            hide_index=True,
            height=400
        )

        # Sekcja "Naucz się więcej"
        with st.expander("📚 Naucz się więcej o każdym wskaźniku"):
            selected_indicator = st.selectbox(
                "Wybierz wskaźnik:",
                options=list(summary.keys())
            )

            if selected_indicator:
                # Map display name to glossary term
                term_map = {
                    'VIX': 'VIX',
                    'SOFR': 'SOFR',
                    'IORB': 'IORB',
                    'Yield Curve (10Y-2Y)': 'YIELD_CURVE',
                    'M2 Money Supply': 'M2',
                    'Financial Conditions': 'NFCI',
                    'Dollar Index (DXY)': 'DXY',
                    'High Yield Spread': 'HY_SPREAD'
                }

                term = term_map.get(selected_indicator, selected_indicator.upper())
                _, short, long, emoji = get_explanation(term)

                st.markdown(f"## {emoji} {selected_indicator}")
                st.markdown(long)

    else:
        st.info("Brak szczegółowych danych wskaźników")

except Exception as e:
    st.error(f"Błąd tworzenia tabeli: {e}")

st.markdown("---")


# ============================================
# PERCENTILE ANALYSIS (Historical Context)
# ============================================

st.markdown("### 📊 Analiza Percentylowa - Kontekst Historyczny")
st.caption("💡 Gdzie obecne wartości są względem historii (0-100%)")

try:
    from utils.percentile_analysis import calculate_percentile, interpret_percentile

    # Lista kluczowych wskaźników do analizy percentylowej
    key_indicators_for_percentile = {
        'VIX': 'vix',
        'SOFR-IORB Spread': 'sofr_iorb_spread',
        'Yield Curve': 'yield_curve',
        'Rezerwy': 'reserves_alt',
        'TGA': 'tga',
        'RRP': 'reverse_repo',
        'M2': 'm2',
        'NFCI': 'nfci'
    }

    # Sprawdź czy mamy dane historyczne
    has_percentile_data = False
    percentile_results = []

    for display_name, indicator_key in key_indicators_for_percentile.items():
        if indicator_key in indicators and 'data' in indicators[indicator_key]:
            ind_data = indicators[indicator_key]

            # Pobierz obecną wartość
            current_val = ind_data.get('current')

            # Pobierz dane historyczne
            historical_data = ind_data['data']['value']

            if current_val is not None and not historical_data.empty:
                # Oblicz percentyl
                percentile = calculate_percentile(current_val, historical_data)

                # Interpretacja
                text, emoji, color = interpret_percentile(indicator_key, percentile)

                percentile_results.append({
                    'Wskaźnik': display_name,
                    'Obecna Wartość': f"{current_val:.2f}" if current_val else "N/A",
                    'Percentyl': f"{percentile:.0f}%",
                    'Status': f"{emoji} {text.split(' - ')[0]}",  # Tylko pierwsza część
                    'Emoji': emoji,
                    'Color': color,
                    'Full_Text': text
                })
                has_percentile_data = True

    if has_percentile_data and percentile_results:
        # Wyświetl w tabeli
        st.markdown("#### 📈 Percentyle Kluczowych Wskaźników")

        # Stwórz DataFrame
        perc_df = pd.DataFrame(percentile_results)

        # Wyświetl tabelę (bez kolumn pomocniczych)
        display_df = perc_df[['Wskaźnik', 'Obecna Wartość', 'Percentyl', 'Status']]
        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True,
            height=350
        )

        # Wyjaśnienie każdego wskaźnika
        with st.expander("🔍 Co oznaczają te percentyle? (kliknij aby rozwinąć)"):
            for _, row in perc_df.iterrows():
                st.markdown(f"**{row['Emoji']} {row['Wskaźnik']}:** {row['Full_Text']}")
                st.markdown("")

        # Wizualizacja percentyli (horizontal bars)
        st.markdown("#### 📊 Wizualizacja Percentyli")

        # Stwórz wykres percentyli
        import plotly.graph_objects as go

        # Przygotuj dane
        indicators_list = [r['Wskaźnik'] for r in percentile_results]
        percentiles_list = [float(r['Percentyl'].replace('%', '')) for r in percentile_results]
        colors_list = []

        # Przypisz kolory bazując na percentylu i typie wskaźnika
        for r in percentile_results:
            perc = float(r['Percentyl'].replace('%', ''))
            # Gradient kolorów
            if perc >= 80:
                color = 'rgba(255, 7, 58, 0.8)'  # Red
            elif perc >= 60:
                color = 'rgba(255, 237, 78, 0.8)'  # Yellow
            elif perc >= 40:
                color = 'rgba(0, 245, 255, 0.8)'  # Cyan
            elif perc >= 20:
                color = 'rgba(255, 237, 78, 0.8)'  # Yellow
            else:
                color = 'rgba(57, 255, 20, 0.8)'  # Green

            colors_list.append(color)

        fig_percentile = go.Figure()

        fig_percentile.add_trace(go.Bar(
            y=indicators_list,
            x=percentiles_list,
            orientation='h',
            marker=dict(
                color=colors_list,
                line=dict(color='rgba(0, 245, 255, 0.3)', width=1)
            ),
            text=[f"{p:.0f}%" for p in percentiles_list],
            textposition='outside',
            textfont=dict(family='Share Tech Mono', size=12)
        ))

        # Dodaj pionowe linie dla quartile'i
        fig_percentile.add_vline(x=25, line_dash="dash", line_color="rgba(255, 255, 255, 0.3)",
                                annotation_text="Q1", annotation_position="top")
        fig_percentile.add_vline(x=50, line_dash="dash", line_color="rgba(255, 255, 255, 0.5)",
                                annotation_text="Mediana", annotation_position="top")
        fig_percentile.add_vline(x=75, line_dash="dash", line_color="rgba(255, 255, 255, 0.3)",
                                annotation_text="Q3", annotation_position="top")

        from components.cyberpunk_theme import apply_chart_theme
        theme_config = apply_chart_theme()
        theme_config.pop('title', None)
        theme_config.pop('xaxis', None)  # Remove xaxis to avoid conflict

        fig_percentile.update_layout(
            **theme_config,
            title="Percentyle Wskaźników (0-100%)",
            xaxis=dict(
                title="Percentyl (%)",
                range=[0, 100],
                gridcolor='rgba(0, 245, 255, 0.1)',
                zerolinecolor='rgba(0, 245, 255, 0.2)'
            ),
            yaxis_title="",
            height=400,
            margin=dict(l=150, r=40, t=60, b=40)
        )

        st.plotly_chart(fig_percentile, use_container_width=True)

        # Edukacyjne wyjaśnienie
        with st.expander("🎓 Jak czytać percentyle? (MUST READ!)"):
            st.markdown("""
            ## 📊 Co to jest percentyl?

            **Percentyl** pokazuje gdzie obecna wartość jest względem całej historii.

            ### 🎯 Przykład (VIX):

            Wyobraź sobie że masz 100 historycznych wartości VIX posortowanych rosnąco:
            ```
            VIX history: [10, 12, 14, 15, 16, 18, 20, 22, 25, 30, 35, 40, ...]
            ```

            **Jeśli obecny VIX = 18:**
            - Jest większy niż ~50% historycznych wartości
            - **Percentyl = 50%** (mediana)
            - Interpretacja: "Typowa wartość, nic nadzwyczajnego"

            **Jeśli obecny VIX = 35:**
            - Jest większy niż ~85% historycznych wartości
            - **Percentyl = 85%** (górne 15%)
            - Interpretacja: "Bardzo wysoko - panika na rynku!"

            ### 📏 Skala Percentyli:

            - **95-100%:** 🔴 Ekstremalnie wysoko (top 5% historii)
            - **75-95%:** 🟠 Bardzo wysoko (górny kwartyl)
            - **55-75%:** 🟡 Wysoko (powyżej mediany)
            - **45-55%:** ⚪ Mediana (typowo)
            - **25-45%:** 🟡 Nisko (poniżej mediany)
            - **5-25%:** 🟢 Bardzo nisko (dolny kwartyl)
            - **0-5%:** 🟢 Ekstremalnie nisko (bottom 5%)

            ### 🎨 Kolory w wykresie:

            **Zależy od wskaźnika!**

            **Dla VIX/Spread (niżej = lepiej):**
            - 🟢 Zielony (0-20%): Super! Nisko = spokój na rynku
            - 🟡 Żółty (20-80%): Normalnie
            - 🔴 Czerwony (80-100%): Źle! Wysoko = panika

            **Dla Rezerw/M2 (wyżej = lepiej):**
            - 🔴 Czerwony (0-20%): Źle! Nisko = brak płynności
            - 🟡 Żółty (20-80%): Normalnie
            - 🟢 Zielony (80-100%): Super! Wysoko = dużo płynności

            ### 💡 Jak to używać?

            **Trading signals:**

            1. **VIX na 90th percentile?**
               → Ekstremalny strach → Czas kupować (contrarian)

            2. **SOFR-IORB spread na 5th percentile?**
               → Repo market spokojny → Risk-on environment → Bullish

            3. **Rezerwy na 20th percentile?**
               → Mało kasy w systemie → Fed może zacząć QE → Watch closely

            4. **M2 na 95th percentile?**
               → Dużo pieniędzy → Inflacja blisko → Fed może podnieść stopy

            ### 🧠 Pro Tip:

            **Mean reversion strategy:**
            - Wskaźniki przy 90%+ percentile → prawdopodobnie wrócą w dół
            - Wskaźniki przy 10%- percentile → prawdopodobnie wrócą w górę

            Ale **UWAGA:** Ekstremalne percentyle mogą trwać długo!
            (Np. VIX był >80th percentile przez 6 miesięcy podczas COVID)

            ### 📚 Kombinacje do śledzenia:

            **Bullish setup:**
            - VIX < 30th percentile (spokój)
            - Rezerwy > 70th percentile (dużo kasy)
            - SOFR spread < 20th percentile (repo działa)
            → **= GREEN LIGHT dla akcji/crypto! 🚀**

            **Bearish setup:**
            - VIX > 70th percentile (strach)
            - Rezerwy < 30th percentile (mało kasy)
            - SOFR spread > 80th percentile (repo stress)
            → **= RED LIGHT - ostrożność! 🛑**
            """)

    else:
        st.info("Brak danych historycznych do obliczenia percentyli. Potrzebne minimum 30 dni historii.")

except Exception as e:
    st.error(f"Błąd analizy percentylowej: {e}")
    import traceback
    st.code(traceback.format_exc())

st.markdown("---")


# ============================================
# LIQUIDITY CHARTS (Time Series)
# ============================================

st.markdown("### 📊 Wykresy Płynności (Historia)")

try:
    # Sprawdź czy mamy dane historyczne
    if 'reserves_alt' in indicators and 'data' in indicators['reserves_alt']:

        # Tab z różnymi wykresami
        chart_tab1, chart_tab2 = st.tabs(["📈 Wszystkie Razem", "🔍 Pojedyncze Wskaźniki"])

        with chart_tab1:
            st.markdown("#### 4 Kluczowe Wskaźniki Płynności")

            # Przygotuj dane dla multi-line chart
            # Musimy stworzyć DataFrame z wszystkimi 4 wskaźnikami
            try:
                base_df = indicators['reserves_alt']['data'][['date']].copy()

                # Dodaj każdy wskaźnik jako kolumnę
                if 'reserves_alt' in indicators and 'data' in indicators['reserves_alt']:
                    reserves_data = indicators['reserves_alt']['data'][['date', 'value']].copy()
                    reserves_data = reserves_data.rename(columns={'value': 'Reserves ($B)'})
                    base_df = base_df.merge(reserves_data, on='date', how='left')

                if 'tga' in indicators and 'data' in indicators['tga']:
                    tga_data = indicators['tga']['data'][['date', 'value']].copy()
                    tga_data = tga_data.rename(columns={'value': 'TGA ($B)'})
                    base_df = base_df.merge(tga_data, on='date', how='left')

                if 'reverse_repo' in indicators and 'data' in indicators['reverse_repo']:
                    rrp_data = indicators['reverse_repo']['data'][['date', 'value']].copy()
                    rrp_data = rrp_data.rename(columns={'value': 'RRP ($B)'})
                    base_df = base_df.merge(rrp_data, on='date', how='left')

                if 'fed_balance' in indicators and 'data' in indicators['fed_balance']:
                    fed_data = indicators['fed_balance']['data'][['date', 'value']].copy()
                    # Fed balance jest w miliardach, więc podziel przez 1000 dla trylionów
                    fed_data['value'] = fed_data['value'] / 1000
                    fed_data = fed_data.rename(columns={'value': 'Fed Balance ($T)'})
                    base_df = base_df.merge(fed_data, on='date', how='left')

                # Stwórz wykres
                y_columns = [col for col in base_df.columns if col != 'date']

                if y_columns:
                    multi_fig = create_multi_line_chart(
                        data=base_df,
                        x_column='date',
                        y_columns=y_columns,
                        title="Wskaźniki Płynności - Historia 90 dni"
                    )
                    st.plotly_chart(multi_fig, use_container_width=True)

                    st.info("""
                    **💡 Jak czytać ten wykres:**
                    - **Reserves up** = Banki mają więcej kasy ✅
                    - **TGA down** = Rząd wydaje kasę (płynność up) ✅
                    - **RRP down** = Kasa wraca z parkingu (płynność up) ✅
                    - **Fed Balance up** = Money printer go BRRR! ✅
                    """)
                else:
                    st.warning("Brak danych do wykresu")

            except Exception as e:
                st.error(f"Błąd tworzenia multi-line chart: {e}")

        with chart_tab2:
            st.markdown("#### Wybierz wskaźnik do szczegółowej analizy")

            chart_indicator = st.selectbox(
                "Wskaźnik:",
                options=[
                    'Rezerwy Banków',
                    'TGA (Treasury)',
                    'Reverse Repo',
                    'Bilans Fed'
                ],
                key='chart_selector'
            )

            # Map wyboru do klucza w indicators
            indicator_map = {
                'Rezerwy Banków': 'reserves_alt',
                'TGA (Treasury)': 'tga',
                'Reverse Repo': 'reverse_repo',
                'Bilans Fed': 'fed_balance'
            }

            selected_key = indicator_map[chart_indicator]

            if selected_key in indicators and 'data' in indicators[selected_key]:
                # Stwórz pojedynczy wykres
                chart_data = indicators[selected_key]['data']

                single_fig = create_time_series(
                    data=chart_data,
                    x_column='date',
                    y_column='value',
                    title=f"{chart_indicator} - Ostatnie 90 dni"
                )
                st.plotly_chart(single_fig, use_container_width=True)

                # Statystyki
                scol1, scol2, scol3, scol4 = st.columns(4)

                with scol1:
                    st.metric("Minimum", f"${chart_data['value'].min():.0f}B")
                with scol2:
                    st.metric("Maksimum", f"${chart_data['value'].max():.0f}B")
                with scol3:
                    st.metric("Średnia", f"${chart_data['value'].mean():.0f}B")
                with scol4:
                    volatility = chart_data['value'].std()
                    st.metric("Zmienność (σ)", f"${volatility:.0f}B")
            else:
                st.warning(f"Brak danych dla {chart_indicator}")

    else:
        st.info("Dane historyczne nie są dostępne dla wykresów")

except Exception as e:
    st.error(f"Błąd ładowania wykresów: {e}")

st.markdown("---")


# ============================================
# EDUCATIONAL SECTION
# ============================================

st.markdown("### 🎓 Mini-Kurs: Płynność Rynkowa")

tab1, tab2, tab3 = st.tabs(["Podstawy", "Repo Market", "QE vs QT"])

with tab1:
    st.markdown("""
    ## Co to jest płynność?

    **Prościej niż się wydaje:**

    Płynność = Ile gotówki jest w systemie finansowym

    ### Wysoka płynność = 🎉
    - Dużo kasy krąży
    - Banki chętnie pożyczają
    - Akcje/crypto rosną (zwykle)
    - Spread SOFR-IORB niski (<10 bps)

    ### Niska płynność = 😬
    - Mało kasy
    - Banki trzymają kasę kurczowo
    - Akcje/crypto spadają (zwykle)
    - Spread SOFR-IORB wysoki (>15 bps)

    ### Skąd się bierze płynność?
    1. **Federal Reserve** - drukuje pieniądze (QE) lub niszczy (QT)
    2. **TGA (Treasury)** - rząd wydaje kasę = płynność up
    3. **Reverse Repo** - spada = kasa wraca na rynek
    4. **Rezerwy bankowe** - ile banki mają w Fedzie

    **Rule of thumb:** Śledź SOFR-IORB spread. To najważniejszy wskaźnik!
    """)

with tab2:
    st.markdown("""
    ## Repo Market = Hydraulika Finansów

    **Co to repo?**

    Repo = Pożyczka zabezpieczona obligacjami (overnight)

    ### Jak działa:
    1. Bank A ma $100M gotówki, ale nie ma obligacji
    2. Bank B ma obligacje, ale potrzebuje $100M na noc
    3. Bank B "sprzedaje" obligacje Bankowi A z umową odkupu jutro
    4. Rano Bank B odkupuje obligacje + płaci odsetki (SOFR rate)

    ### SOFR vs IORB spread = temperatura repo

    - **Spread < 5 bps:** Spokój, wszystko płynne 😊
    - **Spread 10-15 bps:** Lekkie napięcia 😐
    - **Spread 15-20 bps:** Napięcia rosną! 😬
    - **Spread > 20 bps:** REPO STRESS! PANIKA! 🚨

    ### Czemu to ważne?

    Repo to fundament systemu finansowego.
    Jak repo nie działa → cały system zamiera (2008, 2019).

    **Dan Kostecki alert:**
    "Spread SOFR-IORB to #1 wskaźnik płynności. Jak > 20 bps = RUN!"
    """)

with tab3:
    st.markdown("""
    ## QE vs QT = Money Printer

    ### QE (Quantitative Easing) = 🖨️💵

    **"Money printer go BRRR"**

    1. FED kupuje obligacje od banków
    2. Płaci za nie świeżo wydrukowanymi pieniędzmi
    3. Banki mają więcej kasy → płynność rośnie
    4. Bilans Fedu rośnie

    **Efekt:** Akcje/crypto UP! 🚀

    **Przykład COVID (2020):**
    - FED kupił ~$5 TRILLION obligacji
    - S&P500: +60% w rok
    - Bitcoin: $7k → $69k

    ### QT (Quantitative Tightening) = 🔥💵

    **"Money shredder go RRRR"**

    1. FED nie rolluje obligacji (wygasają)
    2. Kasę która dostaje = niszczy
    3. Mniej kasy w systemie → płynność spada
    4. Bilans Fedu spada

    **Efekt:** Akcje/crypto DOWN! 📉

    **Teraz (2024-2025):**
    - FED robi QT od 2022
    - ~$1.5T zniknęło z systemu
    - Stąd napięcia w repo market

    ### TL;DR

    - QE = FED drukuje → wszystko w górę
    - QT = FED niszczy → wszystko w dół
    - Śledź bilans Fedu (FRED: WALCL)
    """)


# ============================================
# SIDEBAR - Glossary Quick Reference
# ============================================

with st.sidebar:
    st.markdown("## 📊 Makro Analysis")
    st.markdown("---")

    st.markdown("### 📚 Szybki Słownik")

    # Top 5 najważniejszych terminów
    top_terms = ['VIX', 'SOFR', 'YIELD_CURVE', 'M2', 'NFCI']

    for term in top_terms:
        full_name, short, _, emoji = get_explanation(term)
        with st.expander(f"{emoji} {term}"):
            st.caption(full_name)
            st.write(short)

    st.markdown("---")

    st.markdown("### 💡 Pro Tips")
    st.markdown("""
    **Top 3 wskaźniki do śledzenia:**

    1. **SOFR-IORB spread**
       - #1 wskaźnik płynności
       - > 20 bps = ALARM!

    2. **VIX**
       - Strach na rynku
       - > 30 = panika

    3. **Yield Curve**
       - Inwersja = recesja blisko
       - 100% hit rate od 1970!
    """)

    st.markdown("---")


# ============================================
# COMPARISON TOOL - OVERLAY CHARTS
# ============================================

st.markdown("### 📊 Narzędzie Porównań - Overlay Charts")
st.caption("💡 Porównaj różne wskaźniki makroekonomiczne na jednym wykresie")

# Available indicators for comparison
available_indicators = {
    # Płynność i VIX
    'vix': 'VIX (Volatility Index)',
    'sofr_iorb_spread': 'SOFR-IORB Spread',
    'repo_rate': 'Repo Rate',
    'reverse_repo': 'Reverse Repo',

    # Obligacje
    'treasury_10y': '10Y Treasury Yield',
    'treasury_2y': '2Y Treasury Yield',
    'hy_spread': 'High Yield Spread',

    # Inflacja
    'cpi': 'CPI (Consumer Price Index)',
    'cpi_core': 'Core CPI',
    'pce': 'PCE (Personal Consumption)',
    'pce_core': 'Core PCE',
    'inflation_5y': '5Y Breakeven Inflation',

    # Stopy procentowe
    'fed_funds': 'Fed Funds Rate',

    # Wzrost gospodarczy
    'gdp_real': 'Real GDP Growth',
    # 'ism_manufacturing': 'ISM Manufacturing',  # DISCONTINUED - removed from FRED 2016
    # 'ism_services': 'ISM Services',            # DISCONTINUED - removed from FRED 2016

    # Inne
    'unemployment': 'Unemployment Rate',
}

# User selection
col_comp1, col_comp2 = st.columns([2, 1])

with col_comp1:
    selected_indicators = st.multiselect(
        "📈 Wybierz wskaźniki do porównania (2-4)",
        options=list(available_indicators.keys()),
        format_func=lambda x: available_indicators[x],
        default=['vix', 'fed_funds', 'cpi'],
        max_selections=4,
        help="Wybierz 2-4 wskaźniki które chcesz porównać na jednym wykresie"
    )

with col_comp2:
    normalize_mode = st.selectbox(
        "⚖️ Tryb normalizacji",
        options=['raw', 'z-score', 'percent'],
        format_func=lambda x: {
            'raw': 'Oryginalne wartości',
            'z-score': 'Z-score (standaryzacja)',
            'percent': '% zmiana od początku'
        }[x],
        help="Jak wyświetlać dane?\n- Raw: Oryginalne wartości\n- Z-score: Standaryzacja (średnia=0, std=1)\n- Percent: % zmiana od pierwszego dnia"
    )

if len(selected_indicators) < 2:
    st.info("👆 Wybierz co najmniej 2 wskaźniki aby zobaczyć porównanie")
elif len(selected_indicators) > 4:
    st.warning("⚠️ Maksymalnie 4 wskaźniki na raz")
else:
    # Build comparison chart
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots

    fig = go.Figure()

    # Track if we have any data
    has_data = False

    # Color palette
    colors = ['#00f5ff', '#ff006e', '#39ff14', '#ffed4e', '#ff8c42']

    for idx, indicator_key in enumerate(selected_indicators):
        indicator_data = indicators.get(indicator_key, {})

        if not indicator_data or not isinstance(indicator_data, dict):
            continue

        # Try to get time series
        history = indicator_data.get('history', [])

        # Check if history is valid (could be list or Series)
        if history is None or (isinstance(history, list) and len(history) == 0):
            continue

        # Convert to DataFrame
        df = pd.DataFrame(history)

        if df.empty or 'date' not in df.columns or 'value' not in df.columns:
            continue

        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date')

        # Apply normalization
        values = df['value'].values

        if normalize_mode == 'z-score':
            # Z-score normalization
            mean_val = values.mean()
            std_val = values.std()
            if std_val > 0:
                values = (values - mean_val) / std_val
        elif normalize_mode == 'percent':
            # Percent change from first value
            first_val = values[0]
            if first_val != 0:
                values = ((values - first_val) / abs(first_val)) * 100

        # Add trace
        fig.add_trace(go.Scatter(
            x=df['date'],
            y=values,
            name=available_indicators[indicator_key],
            line=dict(color=colors[idx % len(colors)], width=2),
            mode='lines',
            hovertemplate='%{y:.2f}<extra></extra>'
        ))

        has_data = True

    if has_data:
        # Update layout
        y_axis_title = {
            'raw': 'Wartość',
            'z-score': 'Z-score (standaryzacja)',
            'percent': '% zmiana od początku'
        }[normalize_mode]

        fig.update_layout(
            title=f"Porównanie wskaźników ({normalize_mode})",
            xaxis_title="Data",
            yaxis_title=y_axis_title,
            hovermode='x unified',
            template='plotly_dark',
            height=500,
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            paper_bgcolor='rgba(10, 14, 39, 0.9)',
            plot_bgcolor='rgba(26, 26, 46, 0.5)',
        )

        st.plotly_chart(fig, use_container_width=True)

        # Interpretation tips
        with st.expander("💡 Jak interpretować porównanie?"):
            st.markdown(f"""
            **Tryb: {normalize_mode.upper()}**

            {'**Oryginalne wartości** - Każdy wskaźnik ma swoją skalę' if normalize_mode == 'raw' else ''}
            {'**Z-score** - Wszystkie wskaźniki są znormalizowane do średniej=0, odchylenie standardowe=1' if normalize_mode == 'z-score' else ''}
            {'**% zmiana** - Pokazuje procentową zmianę względem pierwszego dnia w historii' if normalize_mode == 'percent' else ''}

            🔍 **Co szukać:**
            - **Korelacja dodatnia** - wskaźniki rosną i spadają razem
            - **Korelacja ujemna** - jeden rośnie gdy drugi spada
            - **Leading indicators** - jeden zmienia się przed drugim (np. VIX przed spadkiem akcji)
            - **Divergence** - wskaźniki rozjeżdżają się (może zapowiadać zmianę trendu)

            💡 **Przykłady:**
            - **VIX vs Fed Funds** - Wysokie VIX → Fed obniża stopy (ratowanie rynku)
            - **CPI vs Fed Funds** - Wysoka inflacja → Fed podnosi stopy
            - **10Y vs 2Y Treasury** - Gdy 2Y > 10Y (inwersja) → recesja blisko
            - **ISM vs GDP** - ISM jest leading indicator dla GDP
            """)
    else:
        st.warning("⚠️ Brak danych historycznych dla wybranych wskaźników")

    st.markdown("---")


# ============================================
# LIQUIDITY-TO-ASSET MODEL
# ============================================

st.markdown("### 💰 Liquidity-to-Asset Model")
st.caption("💡 Jak całkowita płynność Fed wpływa na ceny aktywów")

# Calculate total liquidity (reserves + reverse repo)
reserves_val, _ = get_indicator_val('reserves_alt')
rrp_val, _ = get_indicator_val('reverse_repo')

if reserves_val and rrp_val:
    total_liquidity = reserves_val + rrp_val
    st.info(f"📊 **Total Liquidity**: ${total_liquidity:.0f}B (Reserves: ${reserves_val:.0f}B + RRP: ${rrp_val:.0f}B)")
else:
    st.warning("⚠️ Brak danych płynności")
    total_liquidity = None

# Asset selection
available_assets = {
    'BTC-USD': 'Bitcoin',
    'GC=F': 'Gold Futures',
    'SI=F': 'Silver Futures',
    'AAPL': 'Apple Inc.',
    'TSLA': 'Tesla Inc.',
}

col_asset1, col_asset2 = st.columns([2, 1])

with col_asset1:
    selected_asset = st.selectbox(
        "📈 Wybierz aktywo do analizy",
        options=list(available_assets.keys()),
        format_func=lambda x: available_assets[x],
        index=0,  # Default: BTC
        help="Wybierz aktywo aby zobaczyć korelację z płynnością Fed"
    )

with col_asset2:
    lookback_days = st.selectbox(
        "📅 Okres analizy",
        options=[90, 180, 365, 730],
        index=3,  # Default: 730 days (2 years)
        format_func=lambda x: f"{x} dni (~{x//30} mies.)",
        help="Jak daleko wstecz analizować korelację"
    )

if total_liquidity and selected_asset:
    try:
        import yfinance as yf
        import numpy as np
        from scipy import stats

        # Fetch asset price data
        with st.spinner(f"Pobieranie danych dla {available_assets[selected_asset]}..."):
            ticker = yf.Ticker(selected_asset)
            asset_hist = ticker.history(period=f"{lookback_days}d")

        if asset_hist.empty:
            st.error(f"❌ Nie udało się pobrać danych dla {selected_asset}")
        else:
            # Get liquidity historical data (use 'data' key, not 'history')
            # 'history' is just a Series of values, 'data' is DataFrame with date+value columns
            reserves_history = indicators.get('reserves_alt', {}).get('data', pd.DataFrame())
            rrp_history = indicators.get('reverse_repo', {}).get('data', pd.DataFrame())

            # Check if history data is valid (could be list or Series)
            def is_empty_history(hist):
                if hist is None:
                    return True
                if isinstance(hist, list):
                    return len(hist) == 0
                if isinstance(hist, pd.Series) or isinstance(hist, pd.DataFrame):
                    return hist.empty
                return False

            if is_empty_history(reserves_history) or is_empty_history(rrp_history):
                st.warning("⚠️ Brak danych historycznych płynności")
            else:
                # Data is already DataFrame from liquidity_monitor
                df_reserves = reserves_history
                df_rrp = rrp_history

                # Check if DataFrames have required columns
                if df_reserves.empty or 'date' not in df_reserves.columns or 'value' not in df_reserves.columns:
                    st.warning(f"⚠️ Nieprawidłowa struktura danych dla Reserves. Dostępne kolumny: {list(df_reserves.columns)}")
                elif df_rrp.empty or 'date' not in df_rrp.columns or 'value' not in df_rrp.columns:
                    st.warning(f"⚠️ Nieprawidłowa struktura danych dla RRP. Dostępne kolumny: {list(df_rrp.columns)}")
                else:
                    df_reserves['date'] = pd.to_datetime(df_reserves['date'])
                    df_rrp['date'] = pd.to_datetime(df_rrp['date'])

                    # Merge reserves + RRP to get total liquidity
                    df_liquidity = pd.merge(df_reserves, df_rrp, on='date', suffixes=('_reserves', '_rrp'))
                    df_liquidity['total_liquidity'] = df_liquidity['value_reserves'] + df_liquidity['value_rrp']
                    df_liquidity = df_liquidity[['date', 'total_liquidity']]
    
                    # Prepare asset data
                    df_asset = asset_hist.reset_index()
                    df_asset['date'] = pd.to_datetime(df_asset['Date']).dt.tz_localize(None)
                    df_asset = df_asset[['date', 'Close']].rename(columns={'Close': 'price'})
    
                    # Filter by lookback period
                    cutoff_date = datetime.now() - timedelta(days=lookback_days)
                    df_liquidity = df_liquidity[df_liquidity['date'] >= cutoff_date]
                    df_asset = df_asset[df_asset['date'] >= cutoff_date]
    
                    # Merge on date (use asof merge for different frequencies)
                    df_merged = pd.merge_asof(
                        df_asset.sort_values('date'),
                        df_liquidity.sort_values('date'),
                        on='date',
                        direction='backward'
                    ).dropna()
    
                    if len(df_merged) < 10:
                        st.warning("⚠️ Za mało punktów danych do analizy")
                    else:
                        # Calculate correlation
                        correlation = df_merged['price'].corr(df_merged['total_liquidity'])
    
                        # Calculate R-squared (linear regression)
                        slope, intercept, r_value, p_value, std_err = stats.linregress(
                            df_merged['total_liquidity'],
                            df_merged['price']
                        )
                        r_squared = r_value ** 2
    
                        # Display metrics
                        col_m1, col_m2, col_m3 = st.columns(3)
    
                        with col_m1:
                            corr_color = "🟢" if correlation > 0.5 else "🟡" if correlation > 0 else "🔴"
                            st.metric(
                                "Correlation",
                                f"{corr_color} {correlation:.3f}",
                                help="Siła korelacji: >0.7 = silna, 0.3-0.7 = średnia, <0.3 = słaba"
                            )
    
                        with col_m2:
                            st.metric(
                                "R² (R-squared)",
                                f"{r_squared:.3f}",
                                help="Jak dobrze płynność wyjaśnia cenę (0-1, wyżej = lepiej)"
                            )
    
                        with col_m3:
                            significance = "✅ Istotna" if p_value < 0.05 else "⚠️ Nieistotna"
                            st.metric(
                                "P-value",
                                f"{p_value:.4f}",
                                delta=significance,
                                help="P < 0.05 = statystycznie istotna korelacja"
                            )
    
                        # Create dual-axis chart
                        from plotly.subplots import make_subplots
                        import plotly.graph_objects as go
    
                        fig = make_subplots(specs=[[{"secondary_y": True}]])
    
                        # Add asset price (left y-axis)
                        fig.add_trace(
                            go.Scatter(
                                x=df_merged['date'],
                                y=df_merged['price'],
                                name=available_assets[selected_asset],
                                line=dict(color='#00f5ff', width=2),
                                mode='lines'
                            ),
                            secondary_y=False
                        )
    
                        # Add total liquidity (right y-axis)
                        fig.add_trace(
                            go.Scatter(
                                x=df_merged['date'],
                                y=df_merged['total_liquidity'],
                                name='Total Liquidity',
                                line=dict(color='#ff006e', width=2, dash='dot'),
                                mode='lines'
                            ),
                            secondary_y=True
                        )
    
                        # Update layout
                        fig.update_layout(
                            title=f"{available_assets[selected_asset]} vs Total Liquidity",
                            xaxis_title="Data",
                            hovermode='x unified',
                            template='plotly_dark',
                            height=500,
                            paper_bgcolor='rgba(10, 14, 39, 0.9)',
                            plot_bgcolor='rgba(26, 26, 46, 0.5)',
                            legend=dict(
                                orientation="h",
                                yanchor="bottom",
                                y=1.02,
                                xanchor="right",
                                x=1
                            )
                        )
    
                        # Set y-axes titles
                        fig.update_yaxes(title_text=f"{available_assets[selected_asset]} Price", secondary_y=False)
                        fig.update_yaxes(title_text="Total Liquidity ($B)", secondary_y=True)
    
                        st.plotly_chart(fig, use_container_width=True)
    
                        # Interpretation
                        with st.expander("📖 Jak interpretować wyniki?"):
                            st.markdown(f"""
                            **Twoja analiza: {available_assets[selected_asset]} vs Total Liquidity**
    
                            📊 **Wyniki:**
                            - **Correlation**: {correlation:.3f} ({corr_color})
                            - **R²**: {r_squared:.3f} (płynność wyjaśnia {r_squared*100:.1f}% zmienności ceny)
                            - **P-value**: {p_value:.4f} ({significance})
    
                            💡 **Co to znaczy?**
    
                            **Correlation (Korelacja):**
                            - **> 0.7**: Silna dodatnia (płynność ↑ → cena ↑)
                            - **0.3-0.7**: Średnia korelacja
                            - **< 0.3**: Słaba korelacja
                            - **Ujemna**: Odwrotna zależność (płynność ↑ → cena ↓)
    
                            **R² (R-squared):**
                            - Pokazuje jak dobrze płynność "przewiduje" cenę
                            - **R² = 0.80** = 80% zmian ceny wyjaśnione płynnością
                            - **R² = 0.20** = tylko 20% wyjaśnione, inne czynniki ważniejsze
    
                            **P-value:**
                            - **< 0.05**: Korelacja jest statystycznie istotna ✅
                            - **> 0.05**: Może być przypadkowa ⚠️
    
                            🎯 **Praktyczne zastosowanie:**
    
                            {'**Silna korelacja!** Gdy Fed zwiększa płynność (QE, obniżki RRP), cena rośnie. Gdy zmniejsza (QT), cena spada.' if correlation > 0.6 else ''}
                            {'**Średnia korelacja.** Płynność ma wpływ, ale inne czynniki też ważne (sentiment, fundamenty).' if 0.3 <= correlation <= 0.6 else ''}
                            {'**Słaba korelacja.** To aktywo reaguje bardziej na inne czynniki niż na płynność Fed.' if correlation < 0.3 else ''}
    
                            💡 **Dan Kostecki Framework:**
                            - Bitcoin ma zazwyczaj **wysoką korelację** z płynnością (0.7-0.9)
                            - Złoto: średnia korelacja (0.4-0.6)
                            - Tech stocks (AAPL, TSLA): silna w QE, słabsza w QT
    
                            📈 **Trading signal:**
                            {'Jeśli płynność rośnie → rozważ pozycję LONG' if correlation > 0.5 else ''}
                            {'Jeśli płynność spada → rozważ pozycję SHORT lub redukcję ekspozycji' if correlation > 0.5 else ''}
                            """)
    
    except ImportError:
        st.error("❌ Brak biblioteki scipy. Zainstaluj: `pip install scipy`")
    except Exception as e:
        st.error(f"❌ Błąd podczas analizy: {str(e)}")
        import traceback
        st.code(traceback.format_exc())

st.markdown("---")

st.markdown("### 🔄 Cache Info")
st.caption("Dane cache'owane na 1h")
st.caption("FRED aktualizuje raz dziennie")

if st.button("🔄 Odśwież wszystko"):
    st.cache_data.clear()
    st.rerun()


# ============================================
# FOOTER
# ============================================

st.markdown("---")

col_meta1, col_meta2 = st.columns(2)

with col_meta1:
    timestamp = fred_data.get('timestamp', 'Unknown')
    st.caption(f"⏰ Data pobrania: {timestamp}")
    st.caption("📡 Źródło: FRED API (Federal Reserve)")

with col_meta2:
    st.caption("🎓 **Wersja Edukacyjna** - kliknij na wskaźniki aby się uczyć!")
    st.caption("😄 Finanse mogą być zabawne!")
