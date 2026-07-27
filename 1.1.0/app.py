import os
from dotenv import load_dotenv
import streamlit as st

from core.db import init_db
from core.voice import VOICE_INPUT_ENABLED, VOICE_OUTPUT_ENABLED

load_dotenv()

# ---------------------------------------------------
# Page Configuration
# ---------------------------------------------------

st.set_page_config(
    page_title="Reverse Tutor AI",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------
# Database
# ---------------------------------------------------

if "db_initialized" not in st.session_state:
    init_db()
    st.session_state.db_initialized = True

# ---------------------------------------------------
# Theme
# ---------------------------------------------------

if "theme" not in st.session_state:
    st.session_state.theme = "dark"

with st.sidebar:
    st.markdown("## 🎓 Reverse Tutor AI")
    st.caption("Teach • Explain • Master")

    st.divider()

    if st.toggle(
        "🌙 Dark Mode",
        value=st.session_state.theme == "dark",
    ):
        st.session_state.theme = "dark"
    else:
        st.session_state.theme = "light"

theme = st.session_state.theme

# ---------------------------------------------------
# Colors
# ---------------------------------------------------

if theme == "dark":

    BG = "#0F172A"
    CARD = "#1E293B"
    CARD2 = "#172554"
    TEXT = "#F8FAFC"
    SUB = "#94A3B8"
    BORDER = "#334155"

else:

    BG = "#F8FAFC"
    CARD = "#FFFFFF"
    CARD2 = "#EEF2FF"
    TEXT = "#0F172A"
    SUB = "#64748B"
    BORDER = "#CBD5E1"

PRIMARY = "#6366F1"
SUCCESS = "#10B981"
WARNING = "#F59E0B"

# ---------------------------------------------------
# CSS
# ---------------------------------------------------

st.markdown(
    f"""
<style>

@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

html,
body,
[class*="css"] {{

    font-family:'Inter',sans-serif;

}}

.stApp {{

    background:{BG};

}}

section[data-testid="stSidebar"]{{

background:{CARD};

border-right:1px solid {BORDER};

}}

h1,h2,h3,h4,h5{{

color:{TEXT};

}}

p,
span,
label,
div{{

color:{TEXT};

}}

.small-text{{

color:{SUB};
font-size:15px;

}}

.hero{{

background:
linear-gradient(
135deg,
#1E3A8A,
#312E81,
#4F46E5
);

padding:70px;

border-radius:28px;

margin-bottom:35px;

box-shadow:
0 25px 60px rgba(0,0,0,.25);

animation:fadeUp .8s ease;

}}

.hero-title{{

font-size:60px;
font-weight:900;
margin-bottom:15px;

}}

.hero-sub{{

font-size:22px;
color:#E2E8F0;

line-height:1.6;

}}

.badge{{

display:inline-block;

padding:8px 18px;

background:rgba(255,255,255,.15);

border-radius:999px;

font-size:14px;

margin-bottom:20px;

}}

.cta{{

background:white;

color:#1E3A8A;

padding:12px 26px;

border-radius:12px;

font-weight:700;

display:inline-block;

margin-top:25px;

}}

.metric-card{{

background:{CARD};

border:1px solid {BORDER};

padding:25px;

border-radius:18px;

text-align:center;

transition:.3s;

}}

.metric-card:hover{{

transform:translateY(-5px);

box-shadow:0 18px 35px rgba(99,102,241,.25);

}}

.metric-value{{

font-size:34px;

font-weight:800;

}}

.metric-title{{

color:{SUB};

margin-top:8px;

}}

.status-card{{

background:{CARD};

border:1px solid {BORDER};

padding:22px;

border-radius:18px;

}}

.green{{

color:{SUCCESS};

font-weight:700;

}}

.orange{{

color:{WARNING};

font-weight:700;

}}

.mode-card{{

background:{CARD};

border:1px solid {BORDER};

border-radius:22px;

padding:30px;

height:100%;

transition:.3s;

}}

.mode-card:hover{{

transform:translateY(-8px);

border:1px solid {PRIMARY};

box-shadow:0 20px 40px rgba(99,102,241,.30);

}}

.mode-icon{{

font-size:42px;

margin-bottom:18px;

}}

.mode-title{{

font-size:24px;

font-weight:700;

margin-bottom:10px;

}}

.mode-desc{{

color:{SUB};

line-height:1.8;

}}

.footer{{

padding:40px;

text-align:center;

color:{SUB};

}}

@keyframes fadeUp {{

from {{

opacity:0;

transform:translateY(30px);

}}

to {{

opacity:1;

transform:translateY(0);

}}

}}

</style>
""",
    unsafe_allow_html=True,
)

# ---------------------------------------------------
# Sidebar
# ---------------------------------------------------

with st.sidebar:

    st.success("🟢 System Online")

    st.divider()

    st.markdown("### Navigation")

    st.page_link("app.py", label="🏠 Home")

    st.page_link("pages/1_Explain_Mode.py", label="🧠 Explain Mode")

    st.page_link("pages/2_Error_Hunt.py", label="🔍 Error Hunt")

    st.page_link("pages/3_Dashboard.py", label="📊 Dashboard")

    st.page_link("pages/4_Misconception_Library.py", label="📚 Library")

    st.divider()

    st.markdown("### System Status")

    if os.getenv("GEMINI_API_KEY"):
        st.success("Gemini Connected")
    else:
        st.error("Gemini Missing")

    if VOICE_INPUT_ENABLED:
        st.success("Voice Input")
    else:
        st.warning("Voice Input Disabled")

    if VOICE_OUTPUT_ENABLED:
        st.success("Voice Output")
    else:
        st.warning("Voice Output Disabled")

# ---------------------------------------------------
# Hero
# ---------------------------------------------------

left, right = st.columns([1.8, 1])

with left:

    st.markdown(
        """
<div class="hero">

<div class="badge">
🚀 AI Powered Learning Platform
</div>

<div class="hero-title">
Teach to Learn.<br>
Explain to Understand.
</div>

<div class="hero-sub">

Reverse Tutor AI turns traditional learning upside down.

Instead of answering questions, you become the teacher while the AI plays a curious but confused student. Every explanation is analyzed for clarity, misconceptions, and depth of understanding.

</div>

<div class="cta">
🧠 Start Explaining
</div>

</div>
""",
        unsafe_allow_html=True,
    )

with right:

    st.markdown("### Why Reverse Tutor?")

    st.info("🎯 Learn by Teaching")

    st.info("🧠 Misconception Detection")

    st.info("📈 Diagnostic Feedback")

    st.info("🎙️ Voice Conversations")

    st.info("📚 Knowledge Tracking")

st.markdown("<br>", unsafe_allow_html=True)

# ============================================================
# QUICK OVERVIEW
# ============================================================

st.markdown("## 📊 Platform Overview")
st.caption("Everything you need to master concepts by teaching them.")

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.markdown("""
    <div class="metric-card">
        <div class="metric-value">4</div>
        <div class="metric-title">Learning Modes</div>
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown("""
    <div class="metric-card">
        <div class="metric-value">AI</div>
        <div class="metric-title">Gemini Powered</div>
    </div>
    """, unsafe_allow_html=True)

with c3:
    st.markdown("""
    <div class="metric-card">
        <div class="metric-value">🎙️</div>
        <div class="metric-title">Voice Ready</div>
    </div>
    """, unsafe_allow_html=True)

with c4:
    st.markdown("""
    <div class="metric-card">
        <div class="metric-value">SQLite</div>
        <div class="metric-title">Persistent Storage</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ============================================================
# SYSTEM HEALTH
# ============================================================

st.markdown("## 🟢 System Health")

s1, s2, s3 = st.columns(3)

gemini = os.getenv("GEMINI_API_KEY") is not None

with s1:

    if gemini:
        icon = "🟢"
        status = "Connected"
    else:
        icon = "🔴"
        status = "Missing"

    st.markdown(f"""
    <div class="status-card">

    <h3>🤖 Gemini API</h3>

    <p class="green">{icon} {status}</p>

    <p class="small-text">
    Large Language Model powering Reverse Tutor AI.
    </p>

    </div>
    """, unsafe_allow_html=True)

with s2:

    if VOICE_INPUT_ENABLED:
        icon = "🟢"
        status = "Ready"
    else:
        icon = "🟠"
        status = "Disabled"

    st.markdown(f"""
    <div class="status-card">

    <h3>🎙 Voice Input</h3>

    <p class="green">{icon} {status}</p>

    <p class="small-text">
    Explain concepts naturally using your microphone.
    </p>

    </div>
    """, unsafe_allow_html=True)

with s3:

    if VOICE_OUTPUT_ENABLED:
        icon = "🟢"
        status = "Ready"
    else:
        icon = "🟠"
        status = "Disabled"

    st.markdown(f"""
    <div class="status-card">

    <h3>🔊 Voice Output</h3>

    <p class="green">{icon} {status}</p>

    <p class="small-text">
    AI responses can be spoken back to you.
    </p>

    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ============================================================
# LEARNING MODES
# ============================================================

st.markdown("## 🧠 Learning Modes")
st.caption("Choose the experience that best matches your learning style.")

m1, m2 = st.columns(2)

with m1:

    st.markdown("""
    <div class="mode-card">

    <div class="mode-icon">🗣️</div>

    <div class="mode-title">
    Explain Mode
    </div>

    <div class="mode-desc">

    Become the teacher.

    Explain a topic naturally while the AI asks
    progressively deeper questions.

    <br><br>

    ✅ Socratic Dialogue

    <br>

    ✅ Misconception Detection

    <br>

    ✅ Personalized Diagnostic Report

    </div>

    </div>
    """, unsafe_allow_html=True)

    if st.button(
        "🚀 Launch Explain Mode",
        use_container_width=True,
        key="exp",
    ):
        st.switch_page("pages/1_Explain_Mode.py")

with m2:

    st.markdown("""
    <div class="mode-card">

    <div class="mode-icon">🔍</div>

    <div class="mode-title">
    Error Hunt Mode
    </div>

    <div class="mode-desc">

    The AI intentionally makes a subtle mistake.

    Your job is to identify and explain
    why it is incorrect.

    <br><br>

    ✅ Critical Thinking

    <br>

    ✅ Error Identification

    <br>

    ✅ Concept Reinforcement

    </div>

    </div>
    """, unsafe_allow_html=True)

    if st.button(
        "🚀 Launch Error Hunt",
        use_container_width=True,
        key="hunt",
    ):
        st.switch_page("pages/2_Error_Hunt.py")

st.markdown("<br>", unsafe_allow_html=True)

m3, m4 = st.columns(2)

with m3:

    st.markdown("""
    <div class="mode-card">

    <div class="mode-icon">📈</div>

    <div class="mode-title">
    Analytics Dashboard
    </div>

    <div class="mode-desc">

    Track every teaching session.

    Compare confidence against actual
    understanding.

    <br><br>

    ✅ Progress History

    <br>

    ✅ Calibration Gap

    <br>

    ✅ Learning Analytics

    </div>

    </div>
    """, unsafe_allow_html=True)

    if st.button(
        "📊 Open Dashboard",
        use_container_width=True,
        key="dash",
    ):
        st.switch_page("pages/3_Dashboard.py")

with m4:

    st.markdown("""
    <div class="mode-card">

    <div class="mode-icon">📚</div>

    <div class="mode-title">
    Misconception Library
    </div>

    <div class="mode-desc">

    Browse a curated knowledge base
    of common misconceptions collected
    from previous sessions.

    <br><br>

    ✅ Topic Search

    <br>

    ✅ Common Mistakes

    <br>

    ✅ Weak Area Review

    </div>

    </div>
    """, unsafe_allow_html=True)

    if st.button(
        "📖 Open Library",
        use_container_width=True,
        key="library",
    ):
        st.switch_page("pages/4_Misconception_Library.py")

st.markdown("<br><br>", unsafe_allow_html=True)

# ============================================================
# HOW IT WORKS
# ============================================================

st.markdown("## ⚡ How Reverse Tutor Works")

w1, w2, w3, w4 = st.columns(4)

steps = [
    (
        "1️⃣",
        "Choose",
        "Select a topic and begin your learning session."
    ),
    (
        "2️⃣",
        "Teach",
        "Explain the topic as if you were teaching a friend."
    ),
    (
        "3️⃣",
        "Challenge",
        "The AI asks questions and probes for misunderstandings."
    ),
    (
        "4️⃣",
        "Improve",
        "Receive an in-depth report highlighting strengths and weaknesses."
    ),
]

columns = [w1, w2, w3, w4]

for col, step in zip(columns, steps):

    emoji, title, desc = step

    with col:

        st.markdown(f"""
        <div class="mode-card" style="text-align:center;">

        <div style="font-size:46px;">
        {emoji}
        </div>

        <h3>{title}</h3>

        <p class="small-text">
        {desc}
        </p>

        </div>
        """, unsafe_allow_html=True)

st.markdown("<br><br>", unsafe_allow_html=True) 

# ============================================================
# WHY REVERSE TUTOR AI
# ============================================================

st.markdown("## 🌟 Why Reverse Tutor AI?")
st.caption("Learning science meets AI-powered education.")

left, right = st.columns([1.2, 1])

with left:

    st.markdown("""
### Traditional Learning ❌

- Passive reading
- Memorizing definitions
- False confidence
- Easy to forget concepts

---

### Reverse Tutor AI ✅

- Learn by teaching
- AI actively challenges you
- Detect hidden misconceptions
- Receive personalized feedback
- Long-term retention through active recall

This approach is inspired by the **Protégé Effect**—one of the most effective learning techniques, where teaching someone else improves your own understanding.
""")

with right:

    st.info("🧠 Active Recall")
    st.info("🎯 Socratic Questioning")
    st.info("📈 Personalized Feedback")
    st.info("💡 Misconception Detection")
    st.info("🎙️ Voice Conversations")
    st.info("📚 Progress Tracking")

st.markdown("---")

# ============================================================
# FEATURE HIGHLIGHTS
# ============================================================

st.markdown("## 🚀 Feature Highlights")

f1, f2, f3 = st.columns(3)

with f1:
    st.markdown("""
<div class="mode-card">

## 🤖 AI Tutor

The AI intentionally behaves like a curious student,
asking follow-up questions that expose weak understanding.

</div>
""", unsafe_allow_html=True)

with f2:
    st.markdown("""
<div class="mode-card">

## 📊 Smart Analytics

Every session is analyzed to produce
clarity scores,
misconception reports,
and learning trends.

</div>
""", unsafe_allow_html=True)

with f3:
    st.markdown("""
<div class="mode-card">

## 🎙️ Natural Conversations

Support for voice input and spoken responses
creates a realistic teaching experience.

</div>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ============================================================
# TECHNOLOGY STACK
# ============================================================

st.markdown("## ⚙️ Technology Stack")

tech1, tech2, tech3, tech4 = st.columns(4)

with tech1:
    st.metric("Frontend", "Streamlit")

with tech2:
    st.metric("LLM", "Gemini")

with tech3:
    st.metric("Database", "SQLite")

with tech4:
    st.metric("Speech", "gTTS")

st.markdown("<br>", unsafe_allow_html=True)

# ============================================================
# READY TO START
# ============================================================

st.markdown("""
<div class="hero">

<div class="badge">
🎓 Ready to Learn Smarter?
</div>

<div class="hero-title">
Become the Teacher.
</div>

<div class="hero-sub">

Don't just read.

Don't just memorize.

Teach the AI,
discover what you truly understand,
and master concepts through explanation.

</div>

</div>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns([1,1,1])

with col2:

    if st.button(
        "🚀 Start Your First Session",
        use_container_width=True,
        type="primary",
    ):
        st.switch_page("pages/1_Explain_Mode.py")

st.markdown("<br>", unsafe_allow_html=True)

# ============================================================
# FOOTER
# ============================================================

st.markdown("---")

st.markdown(f"""
<div class="footer">

<h3 style="color:{TEXT}; margin-bottom:10px;">
🎓 Reverse Tutor AI
</h3>

<p style="color:{SUB};">

Teach to Learn • Explain to Understand • Discover Misconceptions

</p>

<br>

<div style="display:flex;
justify-content:center;
gap:15px;
flex-wrap:wrap;">

<span style="
background:{CARD};
padding:10px 18px;
border-radius:999px;
border:1px solid {BORDER};">

🤖 Gemini AI

</span>

<span style="
background:{CARD};
padding:10px 18px;
border-radius:999px;
border:1px solid {BORDER};">

🗄 SQLite

</span>

<span style="
background:{CARD};
padding:10px 18px;
border-radius:999px;
border:1px solid {BORDER};">

🎙 Voice Enabled

</span>

<span style="
background:{CARD};
padding:10px 18px;
border-radius:999px;
border:1px solid {BORDER};">

⚡ Streamlit

</span>

</div>

<br>

<p style="color:{SUB}; font-size:14px;">

Built for modern education using AI-powered active learning.

</p>

</div>
""", unsafe_allow_html=True)
