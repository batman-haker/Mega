"""
Mobile-Friendly Navigation Component
Provides top navigation buttons for easy mobile access
"""

import streamlit as st


def render_top_navigation(current_page="Home"):
    """
    Render top navigation bar with page buttons

    Args:
        current_page: Current page name to highlight
    """

    # Mobile-friendly navigation CSS
    st.markdown("""
    <style>
    /* Mobile Top Navigation */
    .mobile-nav-container {
        position: sticky;
        top: 0;
        z-index: 9999;
        background: linear-gradient(90deg, rgba(10, 14, 39, 0.98) 0%, rgba(26, 26, 46, 0.98) 100%);
        padding: 0.5rem 0;
        margin: -1rem -1rem 1rem -1rem;
        border-bottom: 2px solid rgba(0, 245, 255, 0.4);
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.5);
    }

    .mobile-nav-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
        gap: 0.5rem;
        padding: 0 1rem;
        max-width: 100%;
    }

    @media (max-width: 768px) {
        .mobile-nav-grid {
            grid-template-columns: repeat(2, 1fr);
        }
    }

    .nav-button {
        background: rgba(26, 26, 46, 0.8);
        border: 2px solid rgba(0, 245, 255, 0.3);
        border-radius: 8px;
        padding: 0.8rem 0.5rem;
        text-align: center;
        cursor: pointer;
        transition: all 0.3s ease;
        text-decoration: none;
        color: #00f5ff;
        font-family: 'Orbitron', sans-serif;
        font-size: 0.9rem;
        font-weight: 600;
    }

    .nav-button:hover {
        background: rgba(0, 245, 255, 0.2);
        border-color: #00f5ff;
        box-shadow: 0 0 15px rgba(0, 245, 255, 0.4);
        transform: translateY(-2px);
    }

    .nav-button.active {
        background: linear-gradient(90deg, #00f5ff 0%, #00d4ff 100%);
        color: #0a0e27;
        border-color: #00f5ff;
        box-shadow: 0 0 20px rgba(0, 245, 255, 0.6);
    }

    .nav-icon {
        font-size: 1.2rem;
        display: block;
        margin-bottom: 0.2rem;
    }

    .nav-label {
        font-size: 0.75rem;
        display: block;
    }
    </style>
    """, unsafe_allow_html=True)

    # Navigation items
    pages = [
        {"name": "Home", "icon": "🏠", "label": "Home", "url": "/"},
        {"name": "Makro", "icon": "📊", "label": "Makro", "url": "/Makro"},
        {"name": "Stock", "icon": "📈", "label": "Stock", "url": "/Stock"},
        {"name": "AI_Analysis", "icon": "🧠", "label": "AI Analysis", "url": "/AI_Analysis"},
        {"name": "Gra", "icon": "🎮", "label": "Gra", "url": "/Gra"},
    ]

    # Build navigation HTML
    nav_html = '<div class="mobile-nav-container"><div class="mobile-nav-grid">'

    for page in pages:
        active_class = "active" if page["name"] == current_page else ""
        nav_html += f'''
        <a href="{page['url']}" target="_self" class="nav-button {active_class}">
            <span class="nav-icon">{page['icon']}</span>
            <span class="nav-label">{page['label']}</span>
        </a>
        '''

    nav_html += '</div></div>'

    st.markdown(nav_html, unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)


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
