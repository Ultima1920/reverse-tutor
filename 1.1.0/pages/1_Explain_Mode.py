"""
pages/1_Explain_Mode.py — Core Feynman / Reverse Tutoring experience.
 
Flow:
1. Student picks a topic and rates their confidence (1-10)
2. Student types their explanation
3. AI plays a confused peer, asking one probing question per turn
4. After 4 student turns OR 2 consecutive gap_flag=False, a diagnostic report
   is generated and displayed with a colour-coded clarity score card
"""
 
import streamlit as st
import os
from dotenv import load_dotenv
 
load_dotenv()
 
st.set_page_config(
    page_title="Explain Mode — Reverse Tutor AI",
    page_icon="🗣️",
    layout="wide",
)
 
from core import db, ai_engine, persona, calibration, misconceptions
 
# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
 
# Number of student turns before auto-generating the report
MAX_TURNS = 4
# Number of consecutive gap_flag=False before early report generation
EARLY_STOP_CONSECUTIVE = 2
 
 
# ---------------------------------------------------------------------------
# Session state helpers
# ---------------------------------------------------------------------------
 
def _reset_session():
    """Clear all explain-mode session state to start fresh."""
    for key in [
        "em_started", "em_session_id", "em_student_id", "em_topic",
        "em_confidence", "em_history", "em_gap_flags", "em_difficulty",
        "em_report", "em_system_prompt", "em_turn_count",
    ]:
        st.session_state.pop(key, None)
 
 
# Initialise defaults if not already present
if "em_started" not in st.session_state:
    st.session_state["em_started"] = False
if "em_history" not in st.session_state:
    st.session_state["em_history"] = []
if "em_gap_flags" not in st.session_state:
    st.session_state["em_gap_flags"] = []
if "em_difficulty" not in st.session_state:
    st.session_state["em_difficulty"] = "standard"
if "em_turn_count" not in st.session_state:
    st.session_state["em_turn_count"] = 0
if "em_report" not in st.session_state:
    st.session_state["em_report"] = None
 
# Pre-load topic if coming from Dashboard "Re-probe" button
_preloaded_topic = st.session_state.pop("reprobe_topic", None)
 
# ---------------------------------------------------------------------------
# Page header
# ---------------------------------------------------------------------------
st.title("🗣️ Explain Mode")
st.markdown(
    "Explain a concept to **Alex** (your confused AI peer). "
    "Alex will ask one probing question per turn. "
    "After a few turns you'll receive a detailed diagnostic report."
)
st.divider()
 
# ---------------------------------------------------------------------------
# SETUP PANEL (shown before session starts)
# ---------------------------------------------------------------------------
if not st.session_state["em_started"]:
 
    col_setup, col_info = st.columns([2, 1])
 
    with col_setup:
        # Topic input — any subject, not limited to a preset list
        final_topic = st.text_input(
            "📖 What topic do you want to teach Alex?",
            value=_preloaded_topic or "",
            placeholder="e.g. Photosynthesis, the French Revolution, Big-O notation, offside rule in football…",
            key="em_topic_input",
        ).strip()
 
        # Confidence slider
        confidence = st.slider(
            "🎯 Before we start — how well do you think you understand this? (1 = barely, 10 = expert)",
            min_value=1,
            max_value=10,
            value=5,
            key="em_confidence_slider",
        )
 
        # Start button
        if st.button("🚀 Start Session", type="primary", key="em_start_btn"):
            if not final_topic:
                st.error("Please enter a topic before starting.")
            else:
                # Fetch known misconceptions for this topic to guide the AI
                known_mc = misconceptions.get_misconceptions_for_topic(final_topic)
 
                # Build the system prompt with topic + difficulty + known misconceptions
                sys_prompt = persona.get_system_prompt(
                    topic=final_topic,
                    known_misconceptions=known_mc,
                    difficulty="standard",
                )
 
                # Create DB records
                student_id = db.get_or_create_default_student()
                session_id = db.create_session(
                    student_id=student_id,
                    topic=final_topic,
                    mode="explain",
                    self_rated_confidence=confidence,
                )
 
                # Store in session state
                st.session_state.update({
                    "em_started": True,
                    "em_session_id": session_id,
                    "em_student_id": student_id,
                    "em_topic": final_topic,
                    "em_confidence": confidence,
                    "em_history": [],
                    "em_gap_flags": [],
                    "em_difficulty": "standard",
                    "em_system_prompt": sys_prompt,
                    "em_turn_count": 0,
                    "em_report": None,
                })
                st.rerun()
 
    with col_info:
        st.info(
            "**How it works:**\n\n"
            "1. Type any topic — any subject, any level\n"
            "2. Rate your own confidence\n"
            "3. Type your explanation\n"
            "4. Alex will ask one question per turn\n"
            "5. After 4 turns you get a diagnostic report\n\n"
            "The AI never lectures you — it only asks questions."
        )
 
# ---------------------------------------------------------------------------
# ACTIVE SESSION
# ---------------------------------------------------------------------------
else:
    topic = st.session_state["em_topic"]
    turn_count = st.session_state["em_turn_count"]
    gap_flags = st.session_state["em_gap_flags"]
    report = st.session_state["em_report"]
 
    # Session header
    st.markdown(
        f"**Topic:** {topic} &nbsp;|&nbsp; "
        f"**Confidence (self-rated):** {st.session_state['em_confidence']}/10 &nbsp;|&nbsp; "
        f"**Turn:** {turn_count}/{MAX_TURNS}"
    )
 
    # -----------------------------------------------------------------------
    # Render chat history
    # -----------------------------------------------------------------------
    for msg in st.session_state["em_history"]:
        with st.chat_message(
            "user" if msg["role"] == "user" else "assistant",
            avatar="🧑‍🎓" if msg["role"] == "user" else "🤔",
        ):
            st.write(msg["content"])
 
    # -----------------------------------------------------------------------
    # REPORT CARD (if session is complete)
    # -----------------------------------------------------------------------
    if report is not None:
        st.divider()
        st.subheader("📋 Diagnostic Report")
 
        score = report.get("clarity_score", 5)
        # Color-code the score
        if score >= 7:
            score_color = "🟢"
            score_label = "Strong understanding"
        elif score >= 4:
            score_color = "🟡"
            score_label = "Partial understanding"
        else:
            score_color = "🔴"
            score_label = "Significant gaps"
 
        col_score, col_details = st.columns([1, 2])
 
        with col_score:
            st.metric(
                label="Clarity Score",
                value=f"{score_color} {score}/10",
                help=score_label,
            )
            st.caption(score_label)
 
            # Calibration gap
            cal = calibration.compute_calibration_gap(
                st.session_state["em_confidence"], score
            )
            cal_emoji = {"overconfident": "⬇️", "underconfident": "⬆️", "well-calibrated": "✅"}
            st.markdown(
                f"**Self-rated:** {cal['self_rated']}/10 &nbsp;→&nbsp; "
                f"**Actual:** {cal['clarity']}/10\n\n"
                f"{cal_emoji.get(cal['label'], '')} *{cal['label'].replace('-', ' ').title()}*"
            )
 
        with col_details:
            # Correct points
            correct_points = report.get("correct_points", [])
            if correct_points:
                st.markdown("**✅ What you got right:**")
                for pt in correct_points:
                    st.markdown(f"- {pt}")
 
            # Misconception
            misconception = report.get("misconception_found")
            correction = report.get("correct_explanation")
            if misconception:
                st.markdown("**❌ Misconception found:**")
                st.error(misconception)
                if correction:
                    st.markdown("**✅ Correct explanation:**")
                    st.success(correction)
 
            # Weak subtopic
            weak = report.get("weak_subtopic")
            if weak:
                st.markdown(f"**🎯 Weakest sub-topic:** *{weak}*")
 
        st.divider()
        if st.button("🔄 Try Again", type="secondary", key="em_try_again"):
            _reset_session()
            st.rerun()
 
    # -----------------------------------------------------------------------
    # INPUT AREA (only shown while session is active)
    # -----------------------------------------------------------------------
    elif turn_count < MAX_TURNS:
        student_text = ""
 
        chat_val = st.chat_input(
            placeholder="Explain the concept here… (press Enter to send)",
            key=f"em_chat_input_{turn_count}",
        )
        if chat_val:
            student_text = chat_val.strip()
 
        # Process the student's input
        if student_text:
            student_msg = student_text
 
            # Append student message to history
            st.session_state["em_history"].append({"role": "user", "content": student_msg})
 
            # Rebuild system prompt with updated difficulty
            known_mc = misconceptions.get_misconceptions_for_topic(topic)
            sys_prompt = persona.get_system_prompt(
                topic=topic,
                known_misconceptions=known_mc,
                difficulty=st.session_state["em_difficulty"],
            )
 
            # Call the AI
            with st.spinner("Alex is thinking…"):
                result = ai_engine.get_peer_reply(
                    system_prompt=sys_prompt,
                    conversation_history=st.session_state["em_history"],
                )
 
            peer_reply = result.get("peer_reply", "")
            gap_flag = result.get("internal_gap_flag", True)
 
            # Append AI reply to history
            st.session_state["em_history"].append({"role": "assistant", "content": peer_reply})
            st.session_state["em_gap_flags"].append(gap_flag)
            st.session_state["em_turn_count"] += 1
 
            # Adjust difficulty for next turn
            st.session_state["em_difficulty"] = calibration.adjust_difficulty(
                st.session_state["em_gap_flags"]
            )
 
            # Check early stop: 2 consecutive gap_flag=False
            recent = st.session_state["em_gap_flags"][-EARLY_STOP_CONSECUTIVE:]
            early_stop = (
                len(recent) == EARLY_STOP_CONSECUTIVE
                and all(f is False for f in recent)
            )
 
            # Auto-trigger report if max turns reached or early stop
            new_turn = st.session_state["em_turn_count"]
            if new_turn >= MAX_TURNS or early_stop:
                with st.spinner("Generating your diagnostic report…"):
                    report_data = ai_engine.get_diagnostic_report(
                        topic=topic,
                        conversation_history=st.session_state["em_history"],
                    )
 
                # Save to DB
                from core.memory import format_history
                transcript_str = format_history(st.session_state["em_history"])
                db.update_session_result(
                    session_id=st.session_state["em_session_id"],
                    clarity_score=report_data.get("clarity_score", 5),
                    transcript=transcript_str,
                )
 
                # Log concept weakness if one was found
                weak_sub = report_data.get("weak_subtopic")
                if weak_sub:
                    misconceptions.log_concept_weakness(
                        student_id=st.session_state["em_student_id"],
                        topic=topic,
                        sub_concept=weak_sub,
                        clarity_score=report_data.get("clarity_score", 5),
                    )
 
                st.session_state["em_report"] = report_data
 
            st.rerun()
 
    # Reset button always visible during session
    st.divider()
    if st.button("↩️ Start Over", key="em_reset", type="secondary"):
        _reset_session()
        st.rerun()
