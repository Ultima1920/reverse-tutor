import streamlit as st
from core.db import init_db
import os
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="Reverse Tutor AI",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize database on first load (safe to re-run, uses ALTER TABLE)
if "db_initialized" not in st.session_state:
    init_db()
    st.session_state.db_initialized = True

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;900&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

.hero {
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
    border-radius: 20px;
    padding: 48px 40px;
    text-align: center;
    border: 1px solid #2a2a5e;
    margin-bottom: 32px;
}
.hero h1 { font-size: 3rem; font-weight: 900; margin: 0; }
.hero p  { font-size: 1.15rem; color: #a0aec0; margin-top: 12px; }

.mode-card {
    background: linear-gradient(135deg, #1e1e2e, #2a2a3e);
    border: 1px solid #3a3a5c;
    border-radius: 14px;
    padding: 24px;
    height: 100%;
    transition: border-color 0.2s;
}
.mode-card:hover { border-color: #6366f1; }
.mode-card h3 { margin-top: 0; font-size: 1.2rem; }
.mode-card p  { color: #94a3b8; font-size: 0.9rem; }
</style>
""", unsafe_allow_html=True)

# ── Hero Banner ───────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <h1>🎓 Reverse Tutor AI</h1>
    <p>Teach to learn. Explain to understand. The AI plays a confused peer — <em>you</em> are the teacher.</p>
</div>
""", unsafe_allow_html=True)

# ── API Key Warning ───────────────────────────────────────────────────────────
if not os.environ.get("GEMINI_API_KEY"):
    st.warning(
        "⚠️ **GEMINI_API_KEY is not configured.**  \n"
        "Copy `.env.example` to `.env`, add your free Gemini API key, and restart the app.  \n"
        "All AI features will return graceful fallback messages until the key is set."
    )
else:
    st.success("✅ Gemini API key detected — AI features are active.")

# ── Mode Cards ────────────────────────────────────────────────────────────────
st.subheader("📌 Choose a Mode")
c1, c2, c3, c4 = st.columns(4)

with c1:
    st.markdown("""<div class="mode-card">
        <h3>🗣️ Explain Mode</h3>
        <p>Pick a topic and teach it to the AI. After 4 turns you'll receive a full diagnostic report on your clarity and misconceptions.</p>
    </div>""", unsafe_allow_html=True)

with c2:
    st.markdown("""<div class="mode-card">
        <h3>🔍 Error Hunt Mode</h3>
        <p>The AI gives you a mostly-correct explanation with one planted error. Find the mistake to prove you really understand the topic.</p>
    </div>""", unsafe_allow_html=True)

with c3:
    st.markdown("""<div class="mode-card">
        <h3>📊 Dashboard</h3>
        <p>Review your past sessions, see your calibration gap (self-rating vs AI score), and re-probe any weak subtopics.</p>
    </div>""", unsafe_allow_html=True)

with c4:
    st.markdown("""<div class="mode-card">
        <h3>📚 Misconception Library</h3>
        <p>Browse the structured database of common misconceptions that guide the AI's confused-peer persona.</p>
    </div>""", unsafe_allow_html=True)

st.divider()
st.caption("Built with Streamlit · Google Gemini API (free tier) · SQLite · SpeechRecognition · pyttsx3  |  No paid services required.")
