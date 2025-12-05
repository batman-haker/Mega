"""
STOCKANALYZER - Historyczny Inwestor (Gra)

Edukacyjna gra o historycznych kryzysach finansowych.
Epoki: Wielki Kryzys, Stagflacja, DotCom, Black Monday, i więcej!

Uruchomienie:
    streamlit run Home.py
    (wybierz zakładkę "🎮 Gra")
"""

import streamlit as st
import streamlit.components.v1 as components
import sys
from pathlib import Path

# Dodaj katalog stockanalyzer do Python path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

# Import custom modules
from components.cyberpunk_theme import load_cyberpunk_theme
from utils.mobile_styles import inject_mobile_css
from utils.navigation import render_top_navigation


# ============================================
# PAGE CONFIG
# ============================================

st.set_page_config(
    page_title="Historyczny Inwestor - Gra",
    page_icon="🎮",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load cyberpunk theme
load_cyberpunk_theme()

# Inject mobile-responsive CSS
inject_mobile_css()

# Render top navigation
render_top_navigation(current_page="Gra")


# ============================================
# SIDEBAR
# ============================================

with st.sidebar:
    st.markdown("## 🎮 HISTORYCZNY INWESTOR")
    st.markdown("---")

    st.markdown("""
    ### O Grze

    **Edukacyjna gra** o historycznych kryzysach finansowych.

    **Epoki:**
    - 1930s - Wielki Kryzys
    - 1970s - Stagflacja
    - 1987 - Black Monday
    - 1990s - Bull Market
    - 2000-2002 - DotCom
    - 2008 - Subprime
    - I więcej!

    **Poziom trudności:** HARD
    - Obniżone zyski (50-70%)
    - Wyższe straty (30-50%)
    - Koszty: prowizje, podatki
    - Więcej pułapek!

    **Cel:** Przetrwaj kryzysy i pomnóż kapitał!
    """)

    st.markdown("---")

    # Cloud Save/Load (Optional Supabase Integration)
    st.markdown("### ☁️ Zapisz w Chmurze")

    with st.expander("📤 Backup & Restore", expanded=False):
        st.markdown("""
        **Zapisz postęp w chmurze** i graj na różnych urządzeniach!

        ⚠️ **UWAGA:** To funkcja eksperymentalna.
        Gra działa normalnie bez tego - używa lokalnego zapisu.
        """)

        # User ID input
        user_id_input = st.text_input(
            "Twój ID",
            value="",
            placeholder="np. twoj_email@gmail.com",
            help="Użyj unikalnego ID (np. email) aby zidentyfikować swoje zapisy"
        )

        # Save to cloud button
        if st.button("📤 Zapisz do Chmury", use_container_width=True):
            if not user_id_input.strip():
                st.warning("⚠️ Podaj swój ID aby zapisać grę")
            else:
                st.info("🔄 Funkcja w budowie... Zapisywanie do Supabase zostanie wkrótce dodane!")
                # TODO: Implement cloud save
                # 1. Extract localStorage data via JavaScript
                # 2. Save to Supabase using supabase_client.save_game()

        # Load from cloud button
        if st.button("📥 Wczytaj z Chmury", use_container_width=True):
            if not user_id_input.strip():
                st.warning("⚠️ Podaj swój ID aby wczytać grę")
            else:
                st.info("🔄 Funkcja w budowie... Wczytywanie z Supabase zostanie wkrótce dodane!")
                # TODO: Implement cloud load
                # 1. Load from Supabase using supabase_client.list_user_saves()
                # 2. Inject data back to localStorage via JavaScript

    st.markdown("---")

    st.info("💡 **TIP:** Gra uruchamia się poniżej. Przewiń w dół aby zagrać!")


# ============================================
# MAIN CONTENT
# ============================================

# Hero section
st.markdown("""
<div style="text-align: center; padding: 2rem 0;">
    <h1 class="glitch-text">🎮 HISTORYCZNY INWESTOR</h1>
    <p style="font-size: 1.3rem; color: #00f5ff; font-family: 'Orbitron', sans-serif; letter-spacing: 2px;">
        Edukacyjna Gra o Kryzysach Finansowych
    </p>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# Info cards
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    ### 📚 Edukacja

    Ucz się na historycznych przykładach:
    - Wielki Kryzys 1929
    - Stagflacja lat 70.
    - Bańka DotCom 2000
    - Kryzys Subprime 2008
    """)

with col2:
    st.markdown("""
    ### 🎯 Wyzwanie

    Trudny poziom gry:
    - Realistyczne koszty
    - Wyższe ryzyko
    - Pułapki rynkowe
    - Testy psychologiczne
    """)

with col3:
    st.markdown("""
    ### 💰 Strategia

    Podejmuj decyzje:
    - Kiedy kupić?
    - Kiedy sprzedać?
    - Czy grać na spadki?
    - Jak zarządzać kapitałem?
    """)

st.markdown("---")

# Game container with cyberpunk styling
st.markdown("""
<div class="neon-glow" style="padding: 0; margin-top: 2rem; background: rgba(10, 14, 39, 0.8); border-radius: 8px; overflow: hidden;">
""", unsafe_allow_html=True)

# Load and display the game HTML
game_html_path = BASE_DIR / "static" / "game" / "index.html"

try:
    with open(game_html_path, 'r', encoding='utf-8') as f:
        html_content = f.read()

    # Display game in full height with cyberpunk container
    components.html(html_content, height=900, scrolling=True)

except FileNotFoundError:
    st.error(f"""
    ⚠️ **Błąd:** Nie znaleziono pliku gry!

    Oczekiwana lokalizacja: `{game_html_path}`

    Sprawdź czy plik `index.html` znajduje się w katalogu `static/game/`.
    """)
except Exception as e:
    st.error(f"Błąd podczas ładowania gry: {e}")

st.markdown("</div>", unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #606060; font-size: 0.9rem; padding: 2rem 0;">
    <p>🎮 Historyczny Inwestor | Edukacyjna gra o kryzysach finansowych</p>
    <p style="font-size: 0.8rem;">
        Źródło: <a href="https://github.com/batman-haker/historycznyinwestor" target="_blank" style="color: #00f5ff;">GitHub</a>
    </p>
</div>
""", unsafe_allow_html=True)


# ============================================
# DEBUG INFO (tylko w development)
# ============================================

from utils.config import Config

if Config.LOG_LEVEL == "DEBUG":
    with st.expander("🔧 DEBUG INFO"):
        st.write("Game HTML Path:", game_html_path)
        st.write("File exists:", game_html_path.exists())
        st.write("Base Directory:", BASE_DIR)
