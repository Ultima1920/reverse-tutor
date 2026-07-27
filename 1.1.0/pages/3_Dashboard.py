"""
pages/3_Dashboard.py
Reverse Tutor AI Dashboard
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="Dashboard",
    page_icon="📊",
    layout="wide",
)

# ==========================================================
# IMPORTS
# ==========================================================

from core.ui import (
    inject_base_css,
    render_sidebar,
    render_page_header,
    render_metric_card,
    render_info_card,
    render_footer,
)

from core import db

inject_base_css()

render_sidebar()

# ==========================================================
# LOAD DATA
# ==========================================================

student_id = db.get_or_create_default_student()

sessions = db.get_sessions_for_student(student_id)

weaknesses = db.get_unresolved_weaknesses(student_id)

# ==========================================================
# PAGE HEADER
# ==========================================================

render_page_header(
    title="Learning Dashboard",
    subtitle=(
        "Track your learning journey, monitor progress, "
        "and revisit concepts that need more practice."
    ),
    icon="📊",
)

# ==========================================================
# DASHBOARD SUMMARY
# ==========================================================

total_sessions = len(sessions)

completed = [
    s for s in sessions
    if s.get("clarity_score") is not None
]

avg_score = (

    round(

        sum(
            s["clarity_score"]
            for s in completed
        ) / len(completed),

        1,

    )

    if completed

    else 0

)

avg_confidence = (

    round(

        sum(
            s["self_rated_confidence"]
            for s in completed
        ) / len(completed),

        1,

    )

    if completed

    else 0

)

weak_count = len(weaknesses)

# ==========================================================
# KPI CARDS
# ==========================================================

c1, c2, c3, c4 = st.columns(4)

with c1:

    render_metric_card(

        "Sessions",

        total_sessions,

    )

with c2:

    render_metric_card(

        "Average AI Score",

        f"{avg_score}/10",

    )

with c3:

    render_metric_card(

        "Avg Confidence",

        f"{avg_confidence}/10",

    )

with c4:

    render_metric_card(

        "Weak Concepts",

        weak_count,

    )

st.divider()

# ==========================================================
# QUICK INSIGHTS
# ==========================================================

left, right = st.columns([2,1], gap="large")

with left:

    render_info_card(

        "Learning Summary",

        f"""
• Total Sessions : **{total_sessions}**

• Completed Sessions : **{len(completed)}**

• Weak Topics : **{weak_count}**

• Average AI Score : **{avg_score}/10**
""",

        "info",

    )

with right:

    if total_sessions == 0:

        render_info_card(

            "Start Learning",

            "Complete your first Explain Mode session to begin tracking progress.",

            "warning",

        )

    elif avg_score >= 8:

        render_info_card(

            "Excellent",

            "Your explanations show consistently strong conceptual understanding.",

            "success",

        )

    elif avg_score >= 5:

        render_info_card(

            "Good Progress",

            "You're improving. Focus on the weak concepts below.",

            "info",

        )

    else:

        render_info_card(

            "Needs Practice",

            "Spend some time revisiting the concepts marked as weak.",

            "danger",

        )

st.divider()

# ==========================================================
# SESSION HISTORY
# ==========================================================

render_page_header(
    title="Session History",
    subtitle="Review all of your previous learning sessions.",
    icon="📚",
)

if not sessions:

    render_info_card(
        "No Sessions Found",
        "Complete an Explain Mode session to start tracking progress.",
        "warning",
    )

else:

    df = pd.DataFrame(sessions)

    columns = {

        "topic": "Topic",

        "mode": "Mode",

        "self_rated_confidence": "Confidence",

        "clarity_score": "AI Score",

        "started_at": "Date",

    }

    df = df[list(columns.keys())]

    df = df.rename(columns=columns)

    df["Date"] = pd.to_datetime(
        df["Date"],
        errors="coerce",
    ).dt.strftime("%d %b %Y")

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
    )

st.divider()

# ==========================================================
# WEAK CONCEPTS
# ==========================================================

render_page_header(
    title="Weak Concepts",
    subtitle="These concepts need more practice.",
    icon="🎯",
)

if not weaknesses:

    render_info_card(
        "Excellent!",
        "No unresolved weak concepts found.",
        "success",
    )

else:

    for weakness in weaknesses:

        card, button = st.columns(
            [5,1],
            gap="large",
        )

        with card:

            score = weakness.get(
                "last_clarity_score"
            )

            score_text = (
                f"{score}/10"
                if score is not None
                else "N/A"
            )

            render_info_card(

                weakness["topic"],

                f"""
Sub-topic:
**{weakness['sub_concept']}**

Last AI Score:
**{score_text}**
""",

                "warning",

            )

        with button:

            st.write("")
            st.write("")
            st.write("")

            if st.button(

                "Re-Probe",

                key=f"weak_{weakness['id']}",

                use_container_width=True,

            ):

                st.session_state[
                    "reprobe_topic"
                ] = weakness["topic"]

                st.switch_page(
                    "pages/1_Explain_Mode.py"
                )

st.divider()

# ==========================================================
# CALIBRATION ANALYTICS
# ==========================================================

render_page_header(
    title="Confidence Calibration",
    subtitle="Compare your self-confidence with your actual AI clarity scores.",
    icon="📈",
)

chart_sessions = [

    s for s in sessions

    if (
        s.get("self_rated_confidence") is not None
        and
        s.get("clarity_score") is not None
    )

]

if not chart_sessions:

    render_info_card(

        "No Data Yet",

        "Complete an Explain Mode session to unlock analytics.",

        "warning",

    )

else:

    x = [
        s["self_rated_confidence"]
        for s in chart_sessions
    ]

    y = [
        s["clarity_score"]
        for s in chart_sessions
    ]

    topics = [
        s["topic"]
        for s in chart_sessions
    ]

    fig = go.Figure()

    # --------------------------------------------
    # Perfect calibration line
    # --------------------------------------------

    fig.add_trace(

        go.Scatter(

            x=[1,10],

            y=[1,10],

            mode="lines",

            name="Perfect",

            line=dict(
                dash="dash",
                width=2,
            ),

            hoverinfo="skip",

        )

    )

    # --------------------------------------------
    # Session points
    # --------------------------------------------

    fig.add_trace(

        go.Scatter(

            x=x,

            y=y,

            mode="markers+text",

            text=topics,

            textposition="top center",

            marker=dict(

                size=14,

                color=y,

                colorscale="Viridis",

                cmin=1,

                cmax=10,

                colorbar=dict(
                    title="AI Score"
                ),

            ),

            hovertemplate=

            "<b>%{text}</b><br>"

            "Confidence : %{x}/10<br>"

            "AI Score : %{y}/10"

            "<extra></extra>",

        )

    )

    fig.update_layout(

        template="plotly_dark",

        height=500,

        margin=dict(

            l=20,

            r=20,

            t=20,

            b=20,

        ),

        xaxis_title="Self Confidence",

        yaxis_title="AI Clarity Score",

    )

    st.plotly_chart(
        fig,
        use_container_width=True,
    )

    st.divider()

    # ======================================================
    # INSIGHTS
    # ======================================================

    avg_conf = sum(x) / len(x)

    avg_ai = sum(y) / len(y)

    gap = avg_conf - avg_ai

    left, center, right = st.columns(3)

    with left:

        render_metric_card(

            "Average Confidence",

            f"{avg_conf:.1f}/10",

        )

    with center:

        render_metric_card(

            "Average AI Score",

            f"{avg_ai:.1f}/10",

        )

    with right:

        render_metric_card(

            "Calibration Gap",

            f"{gap:+.1f}",

        )

    st.write("")

    if gap > 1:

        render_info_card(

            "⚠ Overconfident",

            """
You usually rate yourself
higher than your actual
performance.

Slow down and explain
concepts with more detail.
""",

            "warning",

        )

    elif gap < -1:

        render_info_card(

            "⬆ Underconfident",

            """
Your understanding is
better than you think.

Trust yourself more.
""",

            "success",

        )

    else:

        render_info_card(

            "✅ Well Calibrated",

            """
Your confidence closely
matches your actual
understanding.

Excellent self-awareness.
""",

            "success",

        )

# ==========================================================
# FOOTER
# ==========================================================

st.divider()

render_footer()
