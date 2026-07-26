"""
app.py — Main entry point for Reverse Tutor AI.
 
This file:
- Configures the Streamlit page
- Loads environment variables from .env
- Initialises the SQLite database on first load
- Displays the welcome/home screen
"""
 
import os
import streamlit as st
from dotenv import load_dotenv
 
from core.ui import inject_base_css, render_hero
 
load_dotenv()
 
# ---------------------------------------------------------------------------
# Page configuration — must be the very first Streamlit call
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Reverse Tutor AI",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)
 
inject_base_css()
 
# ---------------------------------------------------------------------------
# Database initialisation (once per session)
# ---------------------------------------------------------------------------
if "db_initialized" not in st.session_state:
    try:
        from core.db import init_db
        init_db()
        st.session_state["db_initialized"] = True
    except Exception as e:
        st.error(f"⚠️ Database initialisation failed: {e}")
        st.session_state["db_initialized"] = False
 
# ---------------------------------------------------------------------------
# API key check (non-fatal warning)
# ---------------------------------------------------------------------------
api_key = os.environ.get("GEMINI_API_KEY", "").strip()
if not api_key:
    st.warning(
        "🔑 **GEMINI_API_KEY is not set.** AI features (Explain Mode and Error Hunt Mode) "
        "won't work until you:\n"
        "1. Copy `.env.example` → `.env`\n"
        "2. Paste your free Gemini API key from [Google AI Studio](https://aistudio.google.com)\n"
        "3. Restart the Streamlit app\n\n"
        "The Dashboard works without a key.",
        icon="⚠️",
    )
 
# ---------------------------------------------------------------------------
# Hero
# ---------------------------------------------------------------------------
render_hero(
    tagline="The Feynman Technique, made rigorous",
    title="🎓 Reverse Tutor AI",
    subtitle=(
        "You teach. Alex — your confused AI peer — asks the questions. "
        "Explain a concept, get caught on your gaps, and walk away with a "
        "diagnostic report on exactly what you understood and what you didn't."
    ),
)
 
st.divider()
 
# ---------------------------------------------------------------------------
# Mode selection — index cards
# ---------------------------------------------------------------------------
st.markdown("#### Pick a mode")
 
col1, col2, col3 = st.columns(3)
 
with col1:
    st.markdown(
        """<div class="index-card">
            <h3>🗣️ Explain Mode</h3>
            <p>You explain a concept. Alex plays a confused peer who asks one
            probing question per turn. Get a diagnostic report after 4 turns.</p>
        </div>""",
        unsafe_allow_html=True,
    )
    if st.button("Enter Explain Mode →", key="home_explain", type="primary", use_container_width=True):
        st.switch_page("pages/1_Explain_Mode.py")
 
with col2:
    st.markdown(
        """<div class="index-card">
            <h3>🔍 Error Hunt Mode</h3>
            <p>Alex writes a subtly wrong explanation. You find the planted
            factual error. Sharpens critical reading fast.</p>
        </div>""",
        unsafe_allow_html=True,
    )
    if st.button("Enter Error Hunt →", key="home_error", type="primary", use_container_width=True):
        st.switch_page("pages/2_Error_Hunt_Mode.py")
 
with col3:
    st.markdown(
        """<div class="index-card">
            <h3>📊 Dashboard</h3>
            <p>Review past sessions, track clarity scores over time, and
            spot the concepts you keep getting wrong.</p>
        </div>""",
        unsafe_allow_html=True,
    )
    if st.button("Open Dashboard →", key="home_dashboard", type="primary", use_container_width=True):
        st.switch_page("pages/3_Dashboard.py")
 
st.divider()
st.caption(
    "Built with Google Gemini free tier · SQLite · Streamlit — "
    "100% free, no credit card required."
)
 
# ---------------------------------------------------------------------------
# Sidebar navigation hint
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown("## 🎓 Reverse Tutor AI")
    st.markdown(
        "Use the pages above in the sidebar to navigate between modes.\n\n"
        "**Free stack only** — Gemini free tier, SQLite."
    )
    st.divider()
    if api_key:
        st.success("✅ Gemini API key loaded")
    else:
        st.error("❌ No API key — add to .env")
