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
    /* HUGE Mobile Menu Button - JASKRAWO CZERWONY */
    .mobile-menu-btn {
        position: fixed;
        top: 5rem;
        left: 50%;
        transform: translateX(-50%);
        z-index: 9999999999;
        background: linear-gradient(135deg, #ff0000 0%, #ff3333 100%);
        color: #ffffff;
        border: 4px solid #ffff00;
        border-radius: 12px;
        padding: 1rem 1.5rem;
        font-size: 1.8rem;
        font-weight: 900;
        font-family: 'Orbitron', sans-serif;
        box-shadow: 0 0 40px rgba(255, 0, 0, 1), 0 0 20px rgba(255, 255, 0, 0.8);
        cursor: pointer;
        display: flex;
        align-items: center;
        gap: 0.5rem;
        animation: pulse 1s infinite;
        text-shadow: 0 0 10px rgba(255, 255, 0, 1);
    }

    .mobile-menu-btn:active {
        transform: scale(0.95);
    }

    @keyframes pulse {
        0%, 100% {
            box-shadow: 0 0 40px rgba(255, 0, 0, 1), 0 0 20px rgba(255, 255, 0, 0.8);
            transform: scale(1);
        }
        50% {
            box-shadow: 0 0 60px rgba(255, 0, 0, 1), 0 0 40px rgba(255, 255, 0, 1);
            transform: scale(1.05);
        }
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
