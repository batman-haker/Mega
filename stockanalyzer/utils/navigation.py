"""
Mobile-Friendly Navigation Component
Provides top navigation buttons for easy mobile access
"""

import streamlit as st


def render_top_navigation(current_page="Home"):
    """
    Render top navigation bar with page buttons (Streamlit native)

    Args:
        current_page: Current page name to highlight
    """

    # Simple text navigation with markdown
    st.markdown("""
    <div style="background: linear-gradient(90deg, rgba(10, 14, 39, 0.98) 0%, rgba(26, 26, 46, 0.98) 100%);
                padding: 1rem;
                margin: -1rem -1rem 1rem -1rem;
                border-bottom: 2px solid rgba(0, 245, 255, 0.4);
                text-align: center;">
        <span style="color: #00f5ff; font-family: 'Orbitron', sans-serif; font-size: 0.9rem;">
            📱 <strong>Nawigacja:</strong> Użyj menu bocznego (przycisk ◀ w lewym górnym rogu) aby przełączać strony
        </span>
    </div>
    """, unsafe_allow_html=True)


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
