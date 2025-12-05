"""
Mobile-Friendly Navigation Component
Provides top navigation buttons for easy mobile access
"""

import streamlit as st


def render_top_navigation(current_page="Home"):
    """
    Render top navigation bar with page buttons using native Streamlit

    Args:
        current_page: Current page name to highlight
    """

    # Custom CSS for navigation styling
    st.markdown("""
    <style>
    /* Navigation container styling */
    div[data-testid="column"] button {
        width: 100%;
        border-radius: 6px;
        font-family: 'Orbitron', sans-serif;
        font-size: 0.8rem;
        transition: all 0.3s ease;
    }

    /* Top margin adjustment */
    .block-container {
        padding-top: 2rem;
    }

    @media (max-width: 768px) {
        div[data-testid="column"] button {
            font-size: 0.7rem;
            padding: 0.4rem 0.5rem;
        }
    }
    </style>
    """, unsafe_allow_html=True)

    # Page navigation info
    st.markdown("""
    <div style='background: linear-gradient(90deg, rgba(10, 14, 39, 0.98) 0%, rgba(26, 26, 46, 0.98) 100%);
                padding: 0.5rem;
                margin: -1rem -1rem 1rem -1rem;
                border-bottom: 2px solid rgba(0, 245, 255, 0.6);
                text-align: center;'>
        <span style='color: #00f5ff; font-family: "Orbitron", sans-serif; font-size: 0.9rem;'>
            📱 <strong>Nawigacja:</strong> Użyj menu w lewym górnym rogu lub kliknij poniżej
        </span>
    </div>
    """, unsafe_allow_html=True)

    # Create columns for navigation buttons
    cols = st.columns(5)

    pages = [
        ("🏠 Home", "Home.py"),
        ("📊 Makro", "pages/1_📊_Makro.py"),
        ("📈 Stock", "pages/2_📈_Stock.py"),
        ("🧠 AI", "pages/3_🧠_AI_Analysis.py"),
        ("🎮 Gra", "pages/4_🎮_Gra.py")
    ]

    for idx, (page_name, page_path) in enumerate(pages):
        with cols[idx]:
            # Use page_link for proper Streamlit navigation
            is_active = current_page in page_name

            # page_link doesn't support button type, so we'll use custom styling
            if is_active:
                st.markdown(f"""
                <style>
                div[data-testid="column"]:nth-child({idx+1}) a {{
                    background: linear-gradient(135deg, #00f5ff 0%, #00d4ff 100%) !important;
                    color: #000 !important;
                    font-weight: 900 !important;
                }}
                </style>
                """, unsafe_allow_html=True)

            st.page_link(page_path, label=page_name, use_container_width=True)

    st.markdown("---")


def render_mobile_menu_hint():
    """
    Render hint for mobile users about sidebar
    """
    st.markdown("""
    <style>
    .mobile-hint {
        background: rgba(0, 245, 255, 0.1);
        border-left: 4px solid #00f5ff;
        padding: 0.8rem;
        margin: 1rem 0;
        border-radius: 4px;
        display: none;
    }

    @media (max-width: 768px) {
        .mobile-hint {
            display: block;
        }
    }
    </style>

    <div class="mobile-hint">
        💡 <strong>Tip:</strong> Kliknij przycisk w lewym górnym rogu aby otworzyć menu boczne (sidebar)
    </div>
    """, unsafe_allow_html=True)
