"""
STOCKANALYZER - Cyberpunk Theme (Custom CSS)

Profesjonalny cyberpunk design dla Streamlit:
- Dark navy background z gradient
- Neon cyan/magenta accents
- Glitch effects
- Scan-line animations
- Futurystyczne fonty

Użycie:
    from components.cyberpunk_theme import load_cyberpunk_theme

    # W każdej stronie Streamlit:
    load_cyberpunk_theme()
"""

import streamlit as st


def load_cyberpunk_theme():
    """
    Ładuje cyberpunk CSS do aplikacji Streamlit.

    Bez emoji, bez dziecinnych elementów - tylko profesjonalny wygląd.
    """

    st.markdown("""
    <style>
        /* ============================================ */
        /* FONTS */
        /* ============================================ */
        @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Roboto:wght@300;400;500;700&family=Share+Tech+Mono&display=swap');
        @import url('https://fonts.googleapis.com/icon?family=Material+Icons');

        /* ============================================ */
        /* GLOBAL STYLES */
        /* ============================================ */

        /* Main app background - dark gradient */
        .stApp {
            background: linear-gradient(135deg, #0a0e27 0%, #1a1a2e 50%, #0a0e27 100%);
            font-family: 'Roboto', sans-serif;
            color: #e0e0e0;
        }

        /* Scan-line effect overlay */
        .stApp::before {
            content: '';
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: repeating-linear-gradient(
                0deg,
                rgba(0, 245, 255, 0.02) 0px,
                rgba(0, 245, 255, 0.02) 1px,
                transparent 1px,
                transparent 3px
            );
            pointer-events: none;
            z-index: 1;
        }

        /* ============================================ */
        /* TYPOGRAPHY */
        /* ============================================ */

        /* Headers - futuristic Orbitron font */
        h1, h2, h3, h4, h5, h6 {
            font-family: 'Orbitron', sans-serif !important;
            color: #00f5ff !important;
            text-shadow: 0 0 10px rgba(0, 245, 255, 0.5);
            letter-spacing: 1px;
        }

        h1 {
            font-size: 2.5rem !important;
            font-weight: 900 !important;
            text-transform: uppercase;
            margin-bottom: 2rem !important;
        }

        h2 {
            font-size: 1.8rem !important;
            font-weight: 700 !important;
        }

        h3 {
            font-size: 1.4rem !important;
            font-weight: 700 !important;
        }

        /* Body text */
        p, div, span, label {
            font-family: 'Roboto', sans-serif !important;
            color: #e0e0e0 !important;
        }

        /* Monospace for numbers/code */
        code, pre {
            font-family: 'Share Tech Mono', monospace !important;
            background: rgba(0, 245, 255, 0.1) !important;
            border: 1px solid rgba(0, 245, 255, 0.3) !important;
            border-radius: 4px;
            padding: 0.2rem 0.5rem;
        }

        /* ============================================ */
        /* SIDEBAR */
        /* ============================================ */

        [data-testid="stSidebar"] {
            background: rgba(10, 14, 39, 0.98) !important;
            border-right: 2px solid rgba(0, 245, 255, 0.4);
            box-shadow: 5px 0 20px rgba(0, 245, 255, 0.1);
        }

        [data-testid="stSidebar"] h1,
        [data-testid="stSidebar"] h2,
        [data-testid="stSidebar"] h3 {
            color: #ff006e !important;
            text-shadow: 0 0 10px rgba(255, 0, 110, 0.5);
        }

        /* ============================================ */
        /* BUTTONS */
        /* ============================================ */

        /* Primary buttons - neon cyan gradient */
        .stButton>button {
            background: linear-gradient(90deg, #00f5ff 0%, #00d4ff 100%) !important;
            color: #0a0e27 !important;
            border: 2px solid #00f5ff !important;
            border-radius: 6px !important;
            font-family: 'Orbitron', sans-serif !important;
            font-weight: 700 !important;
            font-size: 1rem !important;
            padding: 0.6rem 1.5rem !important;
            text-transform: uppercase;
            letter-spacing: 1px;
            box-shadow: 0 0 20px rgba(0, 245, 255, 0.4);
            transition: all 0.3s ease;
        }

        .stButton>button:hover {
            background: linear-gradient(90deg, #00d4ff 0%, #00f5ff 100%) !important;
            box-shadow: 0 0 30px rgba(0, 245, 255, 0.8);
            transform: translateY(-2px);
        }

        .stButton>button:active {
            transform: translateY(0px);
            box-shadow: 0 0 15px rgba(0, 245, 255, 0.6);
        }

        /* Download button - special magenta */
        .stDownloadButton>button {
            background: linear-gradient(90deg, #ff006e 0%, #ff3385 100%) !important;
            border-color: #ff006e !important;
            box-shadow: 0 0 20px rgba(255, 0, 110, 0.4);
        }

        .stDownloadButton>button:hover {
            box-shadow: 0 0 30px rgba(255, 0, 110, 0.8);
        }

        /* ============================================ */
        /* INPUT FIELDS */
        /* ============================================ */

        /* Text inputs */
        .stTextInput>div>div>input {
            background: rgba(26, 26, 46, 0.9) !important;
            border: 2px solid rgba(0, 245, 255, 0.4) !important;
            color: #e0e0e0 !important;
            border-radius: 6px !important;
            font-family: 'Roboto', sans-serif !important;
            padding: 0.6rem !important;
        }

        .stTextInput>div>div>input:focus {
            border-color: #00f5ff !important;
            box-shadow: 0 0 15px rgba(0, 245, 255, 0.3);
        }

        /* Select boxes */
        .stSelectbox>div>div>select,
        .stSelectbox>div>div>div {
            background: rgba(26, 26, 46, 0.9) !important;
            border: 2px solid rgba(0, 245, 255, 0.4) !important;
            color: #e0e0e0 !important;
            border-radius: 6px !important;
        }

        /* Multiselect */
        .stMultiSelect>div>div {
            background: rgba(26, 26, 46, 0.9) !important;
            border: 2px solid rgba(0, 245, 255, 0.4) !important;
            border-radius: 6px !important;
        }

        /* ============================================ */
        /* METRICS */
        /* ============================================ */

        /* Metric container */
        [data-testid="stMetric"] {
            background: rgba(26, 26, 46, 0.8);
            border: 2px solid rgba(0, 245, 255, 0.3);
            border-radius: 8px;
            padding: 1rem;
            box-shadow: 0 0 15px rgba(0, 245, 255, 0.2);
        }

        /* Metric label */
        [data-testid="stMetricLabel"] {
            font-family: 'Orbitron', sans-serif !important;
            color: #00f5ff !important;
            font-size: 0.9rem !important;
            text-transform: uppercase;
            letter-spacing: 1px;
        }

        /* Metric value - neon numbers */
        [data-testid="stMetricValue"] {
            font-family: 'Share Tech Mono', monospace !important;
            color: #00f5ff !important;
            font-size: 2.2rem !important;
            font-weight: 700 !important;
            text-shadow: 0 0 15px rgba(0, 245, 255, 0.6);
        }

        /* Metric delta (change) */
        [data-testid="stMetricDelta"] {
            font-family: 'Roboto', sans-serif !important;
            font-size: 1rem !important;
        }

        /* ============================================ */
        /* CARDS / CONTAINERS */
        /* ============================================ */

        /* Info/success/warning/error boxes */
        .stAlert {
            background: rgba(26, 26, 46, 0.9) !important;
            border-left: 4px solid #00f5ff !important;
            border-radius: 6px;
            padding: 1rem !important;
        }

        /* Success - green */
        .stSuccess {
            border-left-color: #39ff14 !important;
            background: rgba(57, 255, 20, 0.1) !important;
        }

        /* Warning - yellow */
        .stWarning {
            border-left-color: #ffed4e !important;
            background: rgba(255, 237, 78, 0.1) !important;
        }

        /* Error - red */
        .stError {
            border-left-color: #ff073a !important;
            background: rgba(255, 7, 58, 0.1) !important;
        }

        /* Expandable sections */
        .streamlit-expanderHeader {
            background: rgba(26, 26, 46, 0.8) !important;
            border: 1px solid rgba(0, 245, 255, 0.3) !important;
            border-radius: 6px !important;
            color: #00f5ff !important;
            font-family: 'Orbitron', sans-serif !important;
        }

        .streamlit-expanderHeader:hover {
            background: rgba(26, 26, 46, 1) !important;
            border-color: #00f5ff !important;
        }

        /* ============================================ */
        /* TABLES */
        /* ============================================ */

        /* Dataframe/table styling */
        .dataframe {
            background: rgba(26, 26, 46, 0.8) !important;
            border: 1px solid rgba(0, 245, 255, 0.3) !important;
            border-radius: 6px;
        }

        .dataframe thead tr th {
            background: rgba(0, 245, 255, 0.2) !important;
            color: #00f5ff !important;
            font-family: 'Orbitron', sans-serif !important;
            font-weight: 700 !important;
            border-bottom: 2px solid #00f5ff !important;
        }

        .dataframe tbody tr:hover {
            background: rgba(0, 245, 255, 0.1) !important;
        }

        /* ============================================ */
        /* CHARTS (Plotly) */
        /* ============================================ */

        /* Plotly chart container */
        .js-plotly-plot {
            background: transparent !important;
        }

        /* ============================================ */
        /* TABS */
        /* ============================================ */

        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
            background: rgba(26, 26, 46, 0.6);
            border-radius: 8px;
            padding: 0.5rem;
        }

        .stTabs [data-baseweb="tab"] {
            background: transparent;
            border: 2px solid rgba(0, 245, 255, 0.3);
            border-radius: 6px;
            color: #00f5ff !important;
            font-family: 'Orbitron', sans-serif !important;
            font-weight: 600;
            padding: 0.6rem 1.2rem;
        }

        .stTabs [data-baseweb="tab"]:hover {
            background: rgba(0, 245, 255, 0.1);
            border-color: #00f5ff;
        }

        .stTabs [aria-selected="true"] {
            background: linear-gradient(90deg, #00f5ff 0%, #00d4ff 100%) !important;
            color: #0a0e27 !important;
            box-shadow: 0 0 20px rgba(0, 245, 255, 0.4);
        }

        /* ============================================ */
        /* PROGRESS BAR */
        /* ============================================ */

        .stProgress > div > div > div {
            background: linear-gradient(90deg, #00f5ff 0%, #ff006e 100%) !important;
            box-shadow: 0 0 15px rgba(0, 245, 255, 0.5);
        }

        /* ============================================ */
        /* SPINNER */
        /* ============================================ */

        .stSpinner > div {
            border-color: #00f5ff transparent transparent transparent !important;
        }

        /* ============================================ */
        /* SCROLLBAR */
        /* ============================================ */

        ::-webkit-scrollbar {
            width: 12px;
            height: 12px;
        }

        ::-webkit-scrollbar-track {
            background: rgba(26, 26, 46, 0.8);
        }

        ::-webkit-scrollbar-thumb {
            background: linear-gradient(180deg, #00f5ff 0%, #00d4ff 100%);
            border-radius: 6px;
            border: 2px solid rgba(26, 26, 46, 0.8);
        }

        ::-webkit-scrollbar-thumb:hover {
            background: linear-gradient(180deg, #00d4ff 0%, #00f5ff 100%);
            box-shadow: 0 0 10px rgba(0, 245, 255, 0.5);
        }

        /* ============================================ */
        /* SPECIAL EFFECTS */
        /* ============================================ */

        /* Glitch effect for main title (optional - use in Home.py) */
        .glitch-text {
            font-family: 'Orbitron', sans-serif;
            font-weight: 900;
            font-size: 3rem;
            color: #00f5ff;
            text-transform: uppercase;
            text-shadow:
                0 0 10px rgba(0, 245, 255, 0.8),
                0 0 20px rgba(0, 245, 255, 0.6),
                0 0 30px rgba(255, 0, 110, 0.4);
            animation: glitch 3s infinite;
        }

        @keyframes glitch {
            0%, 90%, 100% {
                text-shadow:
                    0 0 10px rgba(0, 245, 255, 0.8),
                    0 0 20px rgba(0, 245, 255, 0.6),
                    0 0 30px rgba(255, 0, 110, 0.4);
            }
            91% {
                text-shadow:
                    2px 0 10px rgba(255, 0, 110, 0.8),
                    -2px 0 20px rgba(0, 245, 255, 0.6);
            }
            93% {
                text-shadow:
                    -2px 0 10px rgba(0, 245, 255, 0.8),
                    2px 0 20px rgba(255, 0, 110, 0.6);
            }
        }

        /* Neon glow utility class */
        .neon-glow {
            box-shadow: 0 0 20px rgba(0, 245, 255, 0.5);
            border: 2px solid #00f5ff;
            border-radius: 8px;
            padding: 1rem;
            background: rgba(26, 26, 46, 0.8);
        }

    </style>
    """, unsafe_allow_html=True)


def apply_chart_theme() -> dict:
    """
    Zwraca Plotly theme config dla cyberpunk charts.

    Returns:
        dict: Plotly layout config

    Example:
        >>> import plotly.graph_objects as go
        >>> from components.cyberpunk_theme import apply_chart_theme
        >>>
        >>> fig = go.Figure(data=[...])
        >>> fig.update_layout(**apply_chart_theme())
        >>> st.plotly_chart(fig)
    """
    return {
        'plot_bgcolor': 'rgba(26, 26, 46, 0.8)',
        'paper_bgcolor': 'rgba(10, 14, 39, 0.6)',
        'font': {
            'family': 'Roboto, sans-serif',
            'color': '#e0e0e0',
            'size': 12
        },
        'title': {
            'font': {
                'family': 'Orbitron, sans-serif',
                'color': '#00f5ff',
                'size': 18
            }
        },
        'xaxis': {
            'gridcolor': 'rgba(0, 245, 255, 0.1)',
            'linecolor': 'rgba(0, 245, 255, 0.3)',
            'zerolinecolor': 'rgba(0, 245, 255, 0.2)'
        },
        'yaxis': {
            'gridcolor': 'rgba(0, 245, 255, 0.1)',
            'linecolor': 'rgba(0, 245, 255, 0.3)',
            'zerolinecolor': 'rgba(0, 245, 255, 0.2)'
        },
        'legend': {
            'bgcolor': 'rgba(26, 26, 46, 0.9)',
            'bordercolor': 'rgba(0, 245, 255, 0.3)',
            'borderwidth': 1
        }
    }


if __name__ == "__main__":
    print("Cyberpunk theme loaded!")
    print("Use: load_cyberpunk_theme() in your Streamlit pages")
