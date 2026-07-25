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

# ---------------------------------------------------------------------------
# Page configuration — must be the very first Streamlit call
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Reverse Tutor AI",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Load environment variables
# ---------------------------------------------------------------------------
load_dotenv()  # Reads from .env in the project root

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
        "The Dashboard and Misconception Library work without a key.",
        icon="⚠️",
    )

# ---------------------------------------------------------------------------
# Home page content
# ---------------------------------------------------------------------------
st.title("🎓 Reverse Tutor AI")
st.markdown(
    """
    > *"The best way to learn is to teach."* — Richard Feynman

    **Reverse Tutor AI** flips the classroom. Instead of an AI explaining things *to* you,
    *you* explain the concept to the AI — which plays a **curious, confused peer student**
    who asks pointed follow-up questions that expose exactly where your understanding breaks down.

    After a short conversation, you get a **diagnostic report** with a clarity score (1–10)
    and a precise breakdown of your misconceptions.

    This is the **Feynman Technique**, made rigorous and data-driven.
    """
)

st.divider()

# Mode overview cards
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("### 🗣️ Explain Mode")
    st.markdown(
        "You explain a concept. The AI plays a confused peer who asks one "
        "probing question per turn. Get a diagnostic report after 4 turns."
    )
    if st.button("Go to Explain Mode →", key="home_explain"):
        st.switch_page("pages/1_Explain_Mode.py")

with col2:
    st.markdown("### 🔍 Error Hunt Mode")
    st.markdown(
        "The AI writes a subtly wrong explanation. You find the planted "
        "factual error. Great for sharpening critical reading skills."
    )
    if st.button("Go to Error Hunt →", key="home_error"):
        st.switch_page("pages/2_Error_Hunt_Mode.py")

with col3:
    st.markdown("### 📊 Dashboard")
    st.markdown(
        "See all your past sessions. Track clarity scores over time. "
        "Spot your recurring weak concepts and revisit them."
    )
    if st.button("Go to Dashboard →", key="home_dashboard"):
        st.switch_page("pages/3_Dashboard.py")

with col4:
    st.markdown("### 📚 Misconception Library")
    st.markdown(
        "Browse a curated list of common misconceptions by topic. "
        "Understand exactly where students typically go wrong."
    )
    if st.button("Go to Library →", key="home_library"):
        st.switch_page("pages/4_Misconception_Library.py")

st.divider()
st.caption(
    "Built with Google Gemini free tier · SQLite · Streamlit · "
    "SpeechRecognition · pyttsx3 — 100% free, no credit card required."
)

# ---------------------------------------------------------------------------
# Sidebar navigation hint
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown("## 🎓 Reverse Tutor AI")
    st.markdown(
        "Use the pages above in the sidebar to navigate between modes.\n\n"
        "**Free stack only** — Gemini free tier, SQLite, offline voice."
    )
    st.divider()
    if api_key:
        st.success("✅ Gemini API key loaded")
    else:
        st.error("❌ No API key — add to .env")
