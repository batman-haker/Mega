"""
Custom Mobile Menu Button with JavaScript
Forces sidebar toggle on mobile devices
"""

import streamlit as st
import streamlit.components.v1 as components


def render_mobile_menu_button():
    """
    Render a BIG, visible menu button for mobile that forces sidebar toggle
    """

    components.html("""
    <style>
    /* HUGE Mobile Menu Button - always visible */
    .mobile-menu-btn {
        position: fixed;
        top: 1rem;
        left: 1rem;
        z-index: 999999999;
        background: linear-gradient(135deg, #00f5ff 0%, #00d4ff 100%);
        color: #0a0e27;
        border: 3px solid #00f5ff;
        border-radius: 12px;
        padding: 1rem 1.5rem;
        font-size: 1.5rem;
        font-weight: bold;
        font-family: 'Orbitron', sans-serif;
        box-shadow: 0 0 30px rgba(0, 245, 255, 0.8);
        cursor: pointer;
        display: flex;
        align-items: center;
        gap: 0.5rem;
        animation: pulse 2s infinite;
    }

    .mobile-menu-btn:active {
        transform: scale(0.95);
    }

    @keyframes pulse {
        0%, 100% { box-shadow: 0 0 30px rgba(0, 245, 255, 0.8); }
        50% { box-shadow: 0 0 50px rgba(0, 245, 255, 1); }
    }

    /* Hide on desktop */
    @media (min-width: 769px) {
        .mobile-menu-btn {
            display: none;
        }
    }
    </style>

    <button class="mobile-menu-btn" onclick="toggleSidebar()">
        ☰ MENU
    </button>

    <script>
    function toggleSidebar() {
        // Try multiple methods to toggle sidebar

        // Method 1: Find sidebar collapse button and click it
        const collapseButton = document.querySelector('[data-testid="stSidebarCollapseButton"]');
        if (collapseButton) {
            collapseButton.click();
            return;
        }

        // Method 2: Find sidebar and toggle display
        const sidebar = document.querySelector('[data-testid="stSidebar"]');
        if (sidebar) {
            if (sidebar.style.display === 'none' || sidebar.style.visibility === 'hidden') {
                sidebar.style.display = 'block';
                sidebar.style.visibility = 'visible';
                sidebar.style.transform = 'translateX(0)';
            } else {
                sidebar.style.display = 'none';
            }
            return;
        }

        // Method 3: Trigger Streamlit sidebar toggle event
        const sidebarNav = document.querySelector('[data-testid="stSidebarNav"]');
        if (sidebarNav) {
            sidebarNav.click();
        }

        // Method 4: Force sidebar to show using CSS
        const style = document.createElement('style');
        style.innerHTML = `
            [data-testid="stSidebar"] {
                display: block !important;
                visibility: visible !important;
                transform: translateX(0) !important;
            }
        `;
        document.head.appendChild(style);
    }

    // Auto-show sidebar on mobile when page loads
    window.addEventListener('load', function() {
        if (window.innerWidth <= 768) {
            setTimeout(function() {
                const sidebar = document.querySelector('[data-testid="stSidebar"]');
                if (sidebar) {
                    sidebar.style.display = 'block';
                    sidebar.style.visibility = 'visible';
                    sidebar.style.transform = 'translateX(0)';
                }
            }, 100);
        }
    });
    </script>
    """, height=0)
