"""
app.py
Reverse Tutor AI
"""

import os
from dotenv import load_dotenv
import streamlit as st

load_dotenv()

from core.db import init_db
from core.ui import (
    inject_base_css,
    render_sidebar,
    render_page_header,
    render_metric_card,
    render_info_card,
    render_footer,
)

# ==========================================================
# PAGE CONFIG
# ==========================================================

st.set_page_config(
    page_title="Reverse Tutor AI",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_base_css()

# ==========================================================
# INITIALIZE DATABASE
# ==========================================================

if "db_initialized" not in st.session_state:
    init_db()
    st.session_state.db_initialized = True

# ==========================================================
# SIDEBAR
# ==========================================================

render_sidebar()

# ==========================================================
# HERO
# ==========================================================

render_page_header(
    title="Reverse Tutor AI",
    subtitle=(
        "Learn by teaching. Explain concepts to Alex, "
        "receive probing questions, uncover misconceptions, "
        "and master topics through active learning."
    ),
    icon="🎓",
)

# ==========================================================
# QUICK STATS
# ==========================================================

st.markdown("## Platform")

col1, col2, col3, col4 = st.columns(4)

with col1:
    render_metric_card(
        "Learning Modes",
        "4",
    )

with col2:
    render_metric_card(
        "AI Engine",
        "Gemini",
    )

with col3:
    render_metric_card(
        "Database",
        "SQLite",
    )

with col4:
    render_metric_card(
        "Framework",
        "Streamlit",
    )

st.divider()

# ==========================================================
# LEARNING MODES
# ==========================================================

render_page_header(
    title="Choose Your Learning Mode",
    subtitle="Each mode targets a different aspect of understanding.",
)

mode1, mode2 = st.columns(2)
mode3, mode4 = st.columns(2)

with mode1:

    render_info_card(
        "🧠 Explain Mode",
        """
Teach Alex as if you're explaining to a friend.

• AI asks probing questions
• Detects misconceptions
• Gives clarity score
• Personalized diagnostic report

**Best for:** Deep understanding
        """,
        "info",
    )

    if st.button(
        "Open Explain Mode",
        key="home_explain",
        use_container_width=True,
    ):
        st.switch_page("pages/1_Explain_Mode.py")

with mode2:

    render_info_card(
        "🔍 Error Hunt",
        """
Read an explanation containing
one hidden factual mistake.

• Spot the planted error
• Test conceptual accuracy
• Strengthen critical thinking

**Best for:** Revision
        """,
        "warning",
    )

    if st.button(
        "Open Error Hunt",
        key="home_error",
        use_container_width=True,
    ):
        st.switch_page("pages/2_Error_Hunt_Mode.py")

with mode3:

    render_info_card(
        "📊 Dashboard",
        """
Track your learning journey.

• Previous sessions
• Calibration graph
• Weak concepts
• Learning trends

**Best for:** Progress tracking
        """,
        "success",
    )

    if st.button(
        "Open Dashboard",
        key="home_dashboard",
        use_container_width=True,
    ):
        st.switch_page("pages/3_Dashboard.py")

with mode4:

    render_info_card(
        "📚 Misconception Library",
        """
Browse common misconceptions
across different topics.

• Frequent mistakes
• Correct explanations
• Faster revision

**Best for:** Quick review
        """,
        "info",
    )

st.divider()

# ==========================================================
# WHY REVERSE TUTOR AI
# ==========================================================

render_page_header(
    title="Why Reverse Tutor AI?",
    subtitle="Learning science powered by active recall.",
)

left, right = st.columns([2, 1])

with left:

    st.markdown(
        """
### Traditional Learning

- Passive reading
- Memorizing definitions
- False confidence
- Easy to forget concepts

---

### Reverse Tutor AI

- Learn by teaching
- AI challenges your understanding
- Finds misconceptions
- Gives personalized feedback
- Improves long-term retention
"""
    )

with right:

    render_info_card(
        "🧠 Active Recall",
        "Teaching strengthens memory and conceptual understanding.",
        "success",
    )

    render_info_card(
        "🎯 Personalized Feedback",
        "Every session generates targeted suggestions.",
        "info",
    )

    render_info_card(
        "📈 Track Progress",
        "Visualize improvement over multiple sessions.",
        "warning",
    )

st.divider()

# ==========================================================
# TECHNOLOGY STACK
# ==========================================================

render_page_header(
    title="Technology Stack",
    subtitle="Built using modern AI and web technologies.",
)

tech1, tech2, tech3, tech4 = st.columns(4)

with tech1:
    render_metric_card(
        "LLM",
        "Gemini 2.x",
        color="#4285F4",
    )

with tech2:
    render_metric_card(
        "Backend",
        "Python",
        color="#3776AB",
    )

with tech3:
    render_metric_card(
        "Database",
        "SQLite",
        color="#16A34A",
    )

with tech4:
    render_metric_card(
        "Frontend",
        "Streamlit",
        color="#FF4B4B",
    )

st.divider()

# ==========================================================
# GET STARTED
# ==========================================================

render_page_header(
    title="Ready to Test Your Understanding?",
    subtitle=(
        "Start with Explain Mode and let Alex challenge your "
        "knowledge through guided questioning."
    ),
)

cta1, cta2, cta3 = st.columns(3)

with cta1:
    if st.button(
        "🧠 Start Explain Mode",
        use_container_width=True,
        type="primary",
    ):
        st.switch_page("pages/1_Explain_Mode.py")

with cta2:
    if st.button(
        "🔍 Try Error Hunt",
        use_container_width=True,
    ):
        st.switch_page("pages/2_Error_Hunt_Mode.py")

with cta3:
    if st.button(
        "📊 View Dashboard",
        use_container_width=True,
    ):
        st.switch_page("pages/3_Dashboard.py")

st.divider()

# ==========================================================
# FOOTER
# ==========================================================

render_footer()
