import streamlit as st
import pandas as pd
import plotly.express as px
from core.db import get_connection, get_unresolved_weaknesses

st.set_page_config(page_title="Dashboard — Reverse Tutor AI", page_icon="📊", layout="wide")

st.title("📊 Dashboard")
st.caption("Track your teaching performance over time.")

STUDENT_ID = 1  # Default single-student demo mode

# ── Helper: fetch sessions ────────────────────────────────────────────────────
def get_sessions(student_id):
    try:
        conn = get_connection()
        df = pd.read_sql_query(
            """
            SELECT topic, mode, self_rated_confidence, clarity_score,
                   strftime('%Y-%m-%d %H:%M', started_at) as date
            FROM sessions
            WHERE student_id = ?
            ORDER BY started_at DESC
            """,
            conn,
            params=(student_id,)
        )
        conn.close()
        return df
    except Exception as e:
        st.error(f"Could not load sessions: {e}")
        return pd.DataFrame()

# ── Past Sessions Table ───────────────────────────────────────────────────────
st.subheader("📋 Past Sessions")
sessions_df = get_sessions(STUDENT_ID)

if sessions_df.empty:
    st.info("No sessions recorded yet. Complete an **Explain Mode** session to see data here!")
else:
    # Rename for display
    display_df = sessions_df.rename(columns={
        "topic": "Topic",
        "mode": "Mode",
        "self_rated_confidence": "Self-Rating",
        "clarity_score": "AI Clarity Score",
        "date": "Date"
    })
    st.dataframe(display_df, use_container_width=True, hide_index=True)

    # ── Calibration Chart ─────────────────────────────────────────────────────
    st.subheader("📈 Confidence vs. Actual Clarity")
    chart_df = sessions_df.dropna(subset=["self_rated_confidence", "clarity_score"])
    if not chart_df.empty:
        chart_df = chart_df.copy()
        chart_df["self_rated_confidence"] = chart_df["self_rated_confidence"].astype(float)
        chart_df["clarity_score"] = chart_df["clarity_score"].astype(float)

        fig = px.scatter(
            chart_df,
            x="self_rated_confidence",
            y="clarity_score",
            color="topic",
            hover_data=["date"],
            title="Self-Rated Confidence vs. AI Clarity Score",
            labels={
                "self_rated_confidence": "Self-Rated Confidence (1–10)",
                "clarity_score": "AI Clarity Score (1–10)",
                "topic": "Topic"
            },
            template="plotly_dark",
            range_x=[0, 11],
            range_y=[0, 11],
        )
        # Add perfect-calibration diagonal line
        fig.add_shape(
            type="line",
            x0=0, y0=0, x1=10, y1=10,
            line=dict(color="#6366f1", width=2, dash="dash"),
        )
        fig.add_annotation(
            x=8, y=8.5, text="Perfect calibration",
            showarrow=False, font=dict(color="#6366f1", size=11)
        )
        fig.update_layout(height=420, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(30,30,46,0.8)")
        st.plotly_chart(fig, use_container_width=True)

        # Bar chart of average clarity per topic
        avg_df = chart_df.groupby("topic")["clarity_score"].mean().reset_index()
        bar_fig = px.bar(
            avg_df,
            x="topic",
            y="clarity_score",
            color="clarity_score",
            color_continuous_scale="RdYlGn",
            range_color=[1, 10],
            title="Average Clarity Score by Topic",
            labels={"topic": "Topic", "clarity_score": "Avg Clarity Score"},
            template="plotly_dark",
        )
        bar_fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(30,30,46,0.8)")
        st.plotly_chart(bar_fig, use_container_width=True)
    else:
        st.info("Complete at least one full session (with a diagnostic report) to see the calibration chart.")

# ── Unresolved Weaknesses ─────────────────────────────────────────────────────
st.divider()
st.subheader("⚠️ Unresolved Concept Weaknesses")
weaknesses = get_unresolved_weaknesses(STUDENT_ID)

if not weaknesses:
    st.success("🎉 No unresolved weaknesses — great work!")
else:
    for w in weaknesses:
        col1, col2, col3 = st.columns([3, 2, 2])
        with col1:
            st.markdown(f"**{w.get('topic', '—')}** · *{w.get('sub_concept', '—')}*")
        with col2:
            score = w.get("confidence_score", 0)
            st.caption(f"Last clarity score: **{score}/10**")
        with col3:
            if st.button("🔁 Re-probe", key=f"reprobe_{w['id']}"):
                st.session_state["prefill_topic"] = w.get("topic", "")
                st.switch_page("pages/1_Explain_Mode.py")
