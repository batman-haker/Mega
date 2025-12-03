"""
Mobile-Responsive Styles for Streamlit
Provides CSS and helper functions for mobile-friendly UI
"""

import streamlit as st


def inject_mobile_css():
    """Inject mobile-responsive CSS into Streamlit app"""
    st.markdown("""
    <style>
    /* ========================================
       MOBILE RESPONSIVE STYLES
       ======================================== */

    /* Base responsive containers */
    @media (max-width: 768px) {
        /* Main content area */
        .main .block-container {
            padding: 1rem 1rem !important;
            max-width: 100% !important;
        }

        /* Sidebar */
        section[data-testid="stSidebar"] {
            width: 100% !important;
            min-width: 100% !important;
        }

        section[data-testid="stSidebar"] > div {
            width: 100% !important;
        }

        /* Metrics - stack vertically on mobile */
        div[data-testid="metric-container"] {
            min-width: 100% !important;
            flex: 0 0 100% !important;
        }

        /* Columns - stack vertically */
        div[data-testid="column"] {
            width: 100% !important;
            min-width: 100% !important;
            flex: 0 0 100% !important;
        }

        /* Charts */
        .js-plotly-plot {
            width: 100% !important;
        }

        /* Tables */
        table {
            font-size: 12px !important;
        }

        /* Buttons */
        button {
            width: 100% !important;
            margin-bottom: 0.5rem !important;
        }

        /* Select boxes */
        div[data-baseweb="select"] {
            width: 100% !important;
        }

        /* Text inputs */
        input {
            width: 100% !important;
        }

        /* Headers - smaller on mobile */
        h1 {
            font-size: 1.8rem !important;
        }

        h2 {
            font-size: 1.4rem !important;
        }

        h3 {
            font-size: 1.2rem !important;
        }

        /* Expanders */
        div[data-testid="stExpander"] {
            width: 100% !important;
        }

        /* Tabs */
        button[data-baseweb="tab"] {
            width: auto !important;
            font-size: 0.9rem !important;
            padding: 0.5rem 1rem !important;
        }
    }

    /* Tablet responsive (768px - 1024px) */
    @media (min-width: 768px) and (max-width: 1024px) {
        .main .block-container {
            padding: 2rem 1.5rem !important;
        }

        div[data-testid="column"] {
            width: 50% !important;
            flex: 0 0 50% !important;
        }
    }

    /* ========================================
       CUSTOM MOBILE COMPONENTS
       ======================================== */

    /* Mobile-friendly metric cards */
    .mobile-metric {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }

    .mobile-metric h3 {
        color: white;
        font-size: 1rem;
        margin: 0;
        font-weight: 500;
    }

    .mobile-metric .value {
        color: white;
        font-size: 1.8rem;
        font-weight: bold;
        margin: 0.5rem 0;
    }

    .mobile-metric .change {
        color: #b8f5b8;
        font-size: 0.9rem;
    }

    /* Mobile-friendly expert cards */
    .expert-card-mobile {
        background: #1e1e1e;
        border-left: 4px solid #667eea;
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 1rem;
    }

    .expert-card-mobile .expert-name {
        color: #667eea;
        font-weight: bold;
        font-size: 1.1rem;
        margin-bottom: 0.5rem;
    }

    .expert-card-mobile .expert-role {
        color: #888;
        font-size: 0.9rem;
        margin-bottom: 0.8rem;
    }

    .expert-card-mobile .opinion-text {
        color: #ddd;
        font-size: 0.95rem;
        line-height: 1.6;
    }

    /* Mobile navigation buttons */
    .mobile-nav {
        display: flex;
        gap: 0.5rem;
        margin-bottom: 1rem;
        overflow-x: auto;
    }

    .mobile-nav-btn {
        padding: 0.5rem 1rem;
        background: #667eea;
        color: white;
        border-radius: 20px;
        white-space: nowrap;
        font-size: 0.9rem;
    }

    /* Hide on mobile */
    @media (max-width: 768px) {
        .hide-on-mobile {
            display: none !important;
        }
    }

    /* Show only on mobile */
    @media (min-width: 769px) {
        .show-on-mobile {
            display: none !important;
        }
    }

    /* Scrollable horizontal container for mobile */
    .scroll-container-mobile {
        overflow-x: auto;
        white-space: nowrap;
        -webkit-overflow-scrolling: touch;
    }

    .scroll-container-mobile::-webkit-scrollbar {
        height: 6px;
    }

    .scroll-container-mobile::-webkit-scrollbar-thumb {
        background: #667eea;
        border-radius: 10px;
    }
    </style>
    """, unsafe_allow_html=True)


def is_mobile():
    """
    Detect if user is on mobile device
    Note: This is a simple check based on viewport width
    For more accurate detection, use JavaScript
    """
    # In Streamlit, we can't directly detect device
    # But we can use session state to track user preference
    if 'mobile_view' not in st.session_state:
        st.session_state.mobile_view = False
    return st.session_state.mobile_view


def mobile_column_config(mobile_cols=1, tablet_cols=2, desktop_cols=3):
    """
    Return column configuration based on viewport

    Args:
        mobile_cols: Number of columns on mobile (default 1)
        tablet_cols: Number of columns on tablet (default 2)
        desktop_cols: Number of columns on desktop (default 3)

    Returns:
        Number of columns to use
    """
    # For now, default to mobile-friendly single column
    # Can be enhanced with JavaScript detection
    return mobile_cols


def mobile_metric_card(label, value, delta=None, delta_color="normal"):
    """
    Create a mobile-friendly metric card

    Args:
        label: Metric label
        value: Metric value
        delta: Change value (optional)
        delta_color: Color of delta ("normal", "inverse", "off")
    """
    delta_html = ""
    if delta:
        delta_class = "change positive" if "+" in str(delta) else "change negative"
        delta_html = f'<div class="{delta_class}">{delta}</div>'

    st.markdown(f"""
    <div class="mobile-metric">
        <h3>{label}</h3>
        <div class="value">{value}</div>
        {delta_html}
    </div>
    """, unsafe_allow_html=True)


def mobile_expert_opinion(expert_name, expert_role, opinion_text, model_info=None):
    """
    Create a mobile-friendly expert opinion card

    Args:
        expert_name: Name of the expert
        expert_role: Role/specialty of expert
        opinion_text: The expert's opinion
        model_info: Optional model information
    """
    model_html = ""
    if model_info:
        model_html = f'<div style="color: #666; font-size: 0.8rem; margin-top: 0.5rem;">{model_info}</div>'

    st.markdown(f"""
    <div class="expert-card-mobile">
        <div class="expert-name">{expert_name}</div>
        <div class="expert-role">{expert_role}</div>
        <div class="opinion-text">{opinion_text}</div>
        {model_html}
    </div>
    """, unsafe_allow_html=True)


def mobile_view_toggle():
    """Add a toggle to switch between mobile and desktop view"""
    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("📱" if not is_mobile() else "🖥️"):
            st.session_state.mobile_view = not st.session_state.mobile_view
            st.rerun()


def get_responsive_chart_height():
    """Return appropriate chart height based on viewport"""
    return 300 if is_mobile() else 500


def mobile_friendly_dataframe(df, max_rows=10):
    """
    Display dataframe in mobile-friendly way

    Args:
        df: Pandas DataFrame
        max_rows: Maximum rows to display on mobile
    """
    if is_mobile():
        st.dataframe(df.head(max_rows), use_container_width=True, height=300)
    else:
        st.dataframe(df, use_container_width=True)
