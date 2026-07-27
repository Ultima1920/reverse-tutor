"""
pages/3_Dashboard.py — Student progress dashboard for Reverse Tutor AI.
 
Shows:
- Table of all past sessions (topic, mode, clarity score, date)
- List of unresolved concept weaknesses with "Re-probe" buttons
- Plotly scatter chart: self-rated confidence vs. AI clarity score
"""
 
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from dotenv import load_dotenv
 
load_dotenv()
 
st.set_page_config(
    page_title="Dashboard — Reverse Tutor AI",
    page_icon="📊",
    layout="wide",
)
 
from core.ui import inject_base_css, render_topic_chip, CHALK_YELLOW, PEN_RED, SLATE_TEAL, CHALK_SAGE, BG_PANEL
 
inject_base_css()
 
from core import db
 
# ---------------------------------------------------------------------------
# Page header
# ---------------------------------------------------------------------------
st.markdown('<div style="font-family:\'IBM Plex Mono\',monospace;color:var(--chalk-yellow);font-size:0.8rem;letter-spacing:2px;text-transform:uppercase;">Dashboard</div>', unsafe_allow_html=True)
st.title("📊 Your Progress")
st.markdown("Track your progress, spot patterns, and identify what to study next.")
st.divider()
 
# ---------------------------------------------------------------------------
# Load student data (single default student for hackathon demo)
# ---------------------------------------------------------------------------
student_id = db.get_or_create_default_student()
sessions = db.get_sessions_for_student(student_id)
weaknesses = db.get_unresolved_weaknesses(student_id)
 
# ---------------------------------------------------------------------------
# SESSION HISTORY TABLE
# ---------------------------------------------------------------------------
st.subheader("📋 Past Sessions")
 
if not sessions:
    st.info("No sessions yet. Head to **Explain Mode** to complete your first session!")
else:
    # Build a clean dataframe for display
    df = pd.DataFrame(sessions)
 
    # Select and rename columns for display
    display_cols = {
        "topic": "Topic",
        "mode": "Mode",
        "self_rated_confidence": "Self-rated Confidence",
        "clarity_score": "Clarity Score (AI)",
        "started_at": "Date",
    }
    df_display = df[list(display_cols.keys())].rename(columns=display_cols)
 
    # Format dates
    df_display["Date"] = pd.to_datetime(df_display["Date"], errors="coerce").dt.strftime("%Y-%m-%d %H:%M")
 
    # Style the clarity score column with the chalk palette
    def _score_color(val):
        if pd.isna(val) or val is None:
            return ""
        try:
            v = float(val)
            if v >= 7:
                return f"background-color: {SLATE_TEAL}; color: {BG_PANEL}"
            elif v >= 4:
                return f"background-color: {CHALK_YELLOW}; color: {BG_PANEL}"
            else:
                return f"background-color: {PEN_RED}; color: {BG_PANEL}"
        except (ValueError, TypeError):
            return ""
 
    styled = df_display.style.map(_score_color, subset=["Clarity Score (AI)"])
    st.dataframe(styled, use_container_width=True, hide_index=True)
 
# ---------------------------------------------------------------------------
# CONCEPT WEAKNESSES
# ---------------------------------------------------------------------------
st.divider()
st.subheader("🎯 Unresolved Concept Weaknesses")
 
if not weaknesses:
    st.success("✅ No unresolved weaknesses tracked yet. Keep practising!")
else:
    st.markdown("These sub-concepts came up in past sessions where you scored low. Click **Re-probe** to revisit.")
 
    for w in weaknesses:
        with st.container():
            col_info, col_btn = st.columns([4, 1])
            with col_info:
                score = w.get("last_clarity_score")
                score_str = f"{score}/10" if score is not None else "N/A"
                st.markdown(
                    f"{render_topic_chip(w['topic'])} → *{w['sub_concept']}* &nbsp;|&nbsp; "
                    f"Last score: **{score_str}** &nbsp;|&nbsp; "
                    f"Seen: {w.get('last_seen', 'unknown')[:10]}",
                    unsafe_allow_html=True,
                )
            with col_btn:
                if st.button("🔁 Re-probe", key=f"reprobe_{w['id']}"):
                    st.session_state["reprobe_topic"] = w["topic"]
                    st.switch_page("pages/1_Explain_Mode.py")
        st.divider()
 
# ---------------------------------------------------------------------------
# CALIBRATION SCATTER CHART
# ---------------------------------------------------------------------------
st.subheader("📈 Confidence Calibration Chart")
st.markdown(
    "Each dot is a session. **On the diagonal line** = perfectly calibrated. "
    "**Below the line** = overconfident (you rated yourself higher than the AI scored). "
    "**Above the line** = underconfident."
)
 
# Filter sessions that have both values
chart_sessions = [
    s for s in sessions
    if s.get("self_rated_confidence") is not None and s.get("clarity_score") is not None
]
 
if len(chart_sessions) < 1:
    st.info("Complete at least one Explain Mode session to see the calibration chart.")
else:
    x_vals = [s["self_rated_confidence"] for s in chart_sessions]
    y_vals = [s["clarity_score"] for s in chart_sessions]
    labels = [s["topic"] for s in chart_sessions]
 
    fig = go.Figure()
 
    # Reference diagonal line (perfectly calibrated) — dashed chalk line
    fig.add_trace(go.Scatter(
        x=[1, 10],
        y=[1, 10],
        mode="lines",
        name="Perfect calibration",
        line=dict(color=CHALK_SAGE, dash="dash", width=2),
        hoverinfo="skip",
    ))
 
    # Session data points — chalk-yellow to red-pen colorscale
    fig.add_trace(go.Scatter(
        x=x_vals,
        y=y_vals,
        mode="markers+text",
        marker=dict(
            size=16,
            color=y_vals,
            colorscale=[[0, PEN_RED], [0.5, CHALK_YELLOW], [1, SLATE_TEAL]],
            cmin=1,
            cmax=10,
            colorbar=dict(title="Clarity Score", tickfont=dict(color=CHALK_SAGE)),
            line=dict(width=2, color="#10201A"),
        ),
        text=labels,
        textposition="top center",
        textfont=dict(color=CHALK_SAGE, family="Inter"),
        name="Sessions",
        hovertemplate=(
            "<b>%{text}</b><br>"
            "Self-rated: %{x}/10<br>"
            "Clarity: %{y}/10<extra></extra>"
        ),
    ))
 
    fig.update_layout(
        xaxis=dict(
            title="Self-rated Confidence (before session)", range=[0.5, 10.5], dtick=1,
            gridcolor="rgba(168,191,176,0.15)", color=CHALK_SAGE,
        ),
        yaxis=dict(
            title="AI Clarity Score (after session)", range=[0.5, 10.5], dtick=1,
            gridcolor="rgba(168,191,176,0.15)", color=CHALK_SAGE,
        ),
        showlegend=True,
        legend=dict(font=dict(color=CHALK_SAGE)),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=40, r=40, t=20, b=40),
        height=450,
        font=dict(color=CHALK_SAGE),
    )
 
    st.plotly_chart(fig, use_container_width=True)
 
    # Summary stats
    if len(chart_sessions) >= 2:
        avg_self = sum(x_vals) / len(x_vals)
        avg_ai = sum(y_vals) / len(y_vals)
        avg_gap = avg_self - avg_ai
        gap_label = "overconfident" if avg_gap > 1 else ("underconfident" if avg_gap < -1 else "well-calibrated")
        st.caption(
            f"Average self-rating: **{avg_self:.1f}** | Average AI score: **{avg_ai:.1f}** | "
            f"Average gap: **{avg_gap:+.1f}** → *{gap_label}*"
        )
