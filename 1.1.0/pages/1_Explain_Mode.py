"""
pages/1_Explain_Mode.py
Reverse Tutor AI - Explain Mode
"""

import os
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="Explain Mode",
    page_icon="🧠",
    layout="wide",
)

# ==========================================================
# PROJECT IMPORTS
# ==========================================================

from core.ui import (
    inject_base_css,
    render_sidebar,
    render_page_header,
    render_metric_card,
    render_info_card,
    render_turn_dots,
    render_score_badge,
    render_misconception_block,
    render_topic_chip,
    render_footer,
)

from core import (
    ai_engine,
    calibration,
    db,
    misconceptions,
    persona,
)

inject_base_css()

render_sidebar()

# ==========================================================
# CONSTANTS
# ==========================================================

MAX_TURNS = 4
EARLY_STOP_CONSECUTIVE = 2


# ==========================================================
# SESSION RESET
# ==========================================================

def reset_session():
    """Reset Explain Mode."""

    keys = [
        "em_started",
        "em_session_id",
        "em_student_id",
        "em_topic",
        "em_confidence",
        "em_history",
        "em_gap_flags",
        "em_difficulty",
        "em_report",
        "em_system_prompt",
        "em_turn_count",
    ]

    for key in keys:
        st.session_state.pop(key, None)


# ==========================================================
# SESSION DEFAULTS
# ==========================================================

DEFAULTS = {
    "em_started": False,
    "em_history": [],
    "em_gap_flags": [],
    "em_difficulty": "standard",
    "em_turn_count": 0,
    "em_report": None,
}

for key, value in DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = value


# Topic coming from Dashboard

preloaded_topic = st.session_state.pop(
    "reprobe_topic",
    None,
)

# ==========================================================
# HEADER
# ==========================================================

render_page_header(
    title="Explain Mode",
    subtitle=(
        "Teach Alex a concept in your own words. "
        "Alex behaves like a confused peer and asks "
        "probing questions to uncover misconceptions."
    ),
    icon="🧠",
)

# ==========================================================
# INTRODUCTION
# ==========================================================

render_info_card(
    "How it Works",
    """
1. Enter any topic.

2. Rate your confidence.

3. Teach Alex.

4. Alex asks questions.

5. Receive a clarity report with
misconceptions and feedback.
""",
    "info",
)

st.divider()

# ==========================================================
# SETUP SCREEN
# ==========================================================

if not st.session_state["em_started"]:

    left, right = st.columns([2, 1], gap="large")

    # ------------------------------------------------------
    # LEFT PANEL
    # ------------------------------------------------------

    with left:

        render_info_card(
            "Start a New Session",
            "Choose a topic, rate your confidence, and begin teaching Alex.",
            "success",
        )

        topic = st.text_input(
            "📘 Topic",
            value=preloaded_topic or "",
            placeholder="Photosynthesis, Binary Search, Newton's Laws...",
        ).strip()

        confidence = st.slider(
            "🎯 How confident are you?",
            min_value=1,
            max_value=10,
            value=5,
        )

        st.write("")

        start = st.button(
            "🚀 Start Teaching",
            type="primary",
            use_container_width=True,
        )

        # --------------------------------------------------
        # START SESSION
        # --------------------------------------------------

        if start:

            if not topic:

                st.error("Please enter a topic.")

            else:

                # ----------------------------
                # Load misconceptions
                # ----------------------------

                try:

                    known_mc = misconceptions.get_misconceptions_for_topic(
                        topic
                    )

                    if known_mc is None:
                        known_mc = []

                except Exception:

                    known_mc = []

                # ----------------------------
                # Build persona
                # ----------------------------

                try:

                    system_prompt = persona.get_system_prompt(
                        topic=topic,
                        known_misconceptions=known_mc,
                        difficulty="standard",
                    )

                except Exception as e:

                    st.error(f"Persona Error\n\n{e}")

                    st.stop()

                # ----------------------------
                # Create database session
                # ----------------------------

                try:

                    student_id = db.get_or_create_default_student()

                    session_id = db.create_session(
                        student_id=student_id,
                        topic=topic,
                        mode="explain",
                        self_rated_confidence=confidence,
                    )

                except Exception as e:

                    st.error(f"Database Error\n\n{e}")

                    st.stop()

                # ----------------------------
                # Save session state
                # ----------------------------

                st.session_state.update(

                    {

                        "em_started": True,

                        "em_session_id": session_id,

                        "em_student_id": student_id,

                        "em_topic": topic,

                        "em_confidence": confidence,

                        "em_history": [],

                        "em_gap_flags": [],

                        "em_turn_count": 0,

                        "em_report": None,

                        "em_difficulty": "standard",

                        "em_system_prompt": system_prompt,

                    }

                )

                st.rerun()

    # ------------------------------------------------------
    # RIGHT PANEL
    # ------------------------------------------------------

    with right:

        render_info_card(
            "💡 Reverse Tutoring",
            """
Alex never lectures.

Alex only asks questions.

The goal is to expose gaps in your
understanding instead of testing memory.
""",
            "info",
        )

        render_info_card(
            "📋 Session Details",
            f"""
• Maximum Turns : **{MAX_TURNS}**

• Difficulty adapts automatically

• AI evaluates clarity

• Personalized report

• Calibration analysis
""",
            "warning",
        )

        render_info_card(
            "🏆 Tips",
            """
✔ Explain in your own words.

✔ Use examples.

✔ Avoid memorized definitions.

✔ Imagine teaching a junior student.
""",
            "success",
        )

    st.divider()

# ==========================================================
# ACTIVE SESSION
# ==========================================================

else:

    topic = st.session_state["em_topic"]
    confidence = st.session_state["em_confidence"]
    turn = st.session_state["em_turn_count"]
    report = st.session_state["em_report"]
    history = st.session_state["em_history"]
    gap_flags = st.session_state["em_gap_flags"]

    # ------------------------------------------------------
    # SESSION HEADER
    # ------------------------------------------------------

    render_page_header(
        title=f"Teaching Alex • {topic}",
        subtitle="Keep explaining until Alex is convinced you truly understand the topic.",
        icon="🎓",
    )

    # ------------------------------------------------------
    # SESSION METRICS
    # ------------------------------------------------------

    metric1, metric2, metric3 = st.columns(3)

    with metric1:
        render_metric_card(
            "📘 Topic",
            topic,
        )

    with metric2:
        render_metric_card(
            "🎯 Confidence",
            f"{confidence}/10",
        )

    with metric3:
        render_metric_card(
            "💬 Progress",
            f"{turn}/{MAX_TURNS}",
        )

    render_turn_dots(turn, MAX_TURNS)

    st.divider()

    # ------------------------------------------------------
    # CHAT SECTION
    # ------------------------------------------------------

    render_info_card(
        "Conversation",
        "Explain naturally. Alex will ask one question after every response.",
        "info",
    )

    chat_container = st.container()

    with chat_container:

        if len(history) == 0:

            render_info_card(
                "Alex",
                f"""
Hi! 👋

I'm Alex.

Pretend I'm your classmate.

Can you teach me **{topic}** from the beginning?

Assume I know almost nothing.
""",
                "success",
            )

        else:

            for msg in history:

                if msg["role"] == "user":

                    render_chat_card(
                        "user",
                        msg["content"],
                    )

                else:

                    render_chat_card(
                        "assistant",
                        msg["content"],
                    )

    st.divider()
# ==========================================================
# STUDENT INPUT
# ==========================================================

    if report is None and turn < MAX_TURNS:

        render_info_card(
            "✍️ Your Turn",
            "Explain the concept in your own words. Alex is listening carefully.",
            "warning",
        )

        student_text = st.text_area(
            "Your Explanation",
            key=f"em_text_{turn}",
            height=180,
            placeholder="""
Imagine Alex is sitting next to you.

Don't write textbook definitions.

Teach naturally using examples and simple language.
""",
        )

        send_col1, send_col2 = st.columns([5, 1])

        with send_col2:

            send_clicked = st.button(
                "Send ➜",
                type="primary",
                use_container_width=True,
            )

        if send_clicked:

            if not student_text.strip():

                st.warning(
                    "Please explain something before sending."
                )

            else:

                # ------------------------------------------
                # SAVE USER MESSAGE
                # ------------------------------------------

                history.append(

                    {
                        "role": "user",
                        "content": student_text.strip(),
                    }

                )

                st.session_state["em_history"] = history

                # ------------------------------------------
                # REFRESH MISCONCEPTIONS
                # ------------------------------------------

                try:

                    known_mc = misconceptions.get_misconceptions_for_topic(
                        topic
                    )

                    if known_mc is None:
                        known_mc = []

                except Exception:

                    known_mc = []

                # ------------------------------------------
                # BUILD SYSTEM PROMPT
                # ------------------------------------------

                try:

                    system_prompt = persona.get_system_prompt(

                        topic=topic,

                        known_misconceptions=known_mc,

                        difficulty=st.session_state[
                            "em_difficulty"
                        ],

                    )

                except Exception as e:

                    st.error(f"Prompt Error\n\n{e}")

                    st.stop()

                # ------------------------------------------
                # CALL AI
                # ------------------------------------------

                with st.spinner("Alex is thinking..."):

                    result = ai_engine.get_peer_reply(

                        system_prompt=system_prompt,

                        conversation_history=history,

                    )

                peer_reply = result.get(
                    "peer_reply",
                    "",
                )

                gap_flag = result.get(
                    "internal_gap_flag",
                    True,
                )

                # ------------------------------------------
                # SAVE AI RESPONSE
                # ------------------------------------------

                history.append(

                    {
                        "role": "assistant",
                        "content": peer_reply,
                    }

                )

                st.session_state["em_history"] = history

                gap_flags.append(gap_flag)

                st.session_state[
                    "em_gap_flags"
                ] = gap_flags

                st.session_state[
                    "em_turn_count"
                ] += 1
                # ==========================================
                # ADAPT DIFFICULTY
                # ==========================================

                st.session_state["em_difficulty"] = (
                    calibration.adjust_difficulty(
                        st.session_state["em_gap_flags"]
                    )
                )

                # ==========================================
                # EARLY STOP CHECK
                # ==========================================

                recent_flags = st.session_state[
                    "em_gap_flags"
                ][-EARLY_STOP_CONSECUTIVE:]

                early_stop = (

                    len(recent_flags)
                    == EARLY_STOP_CONSECUTIVE

                    and

                    all(flag is False for flag in recent_flags)

                )

                current_turn = st.session_state[
                    "em_turn_count"
                ]

                report_required = (

                    current_turn >= MAX_TURNS

                    or

                    early_stop

                )
                # ==========================================
                # GENERATE DIAGNOSTIC REPORT
                # ==========================================

                if report_required:

                    with st.spinner(
                        "Generating your personalized report..."
                    ):

                        report_data = (
                            ai_engine.get_diagnostic_report(
                                topic=topic,
                                conversation_history=history,
                            )
                        )

                    st.session_state["em_report"] = report_data

                    report = report_data
                    # ==========================================
                    # SAVE SESSION TO DATABASE
                    # ==========================================

                    from core.memory import format_history

                    transcript = format_history(history)

                    db.update_session_result(

                        session_id=st.session_state[
                            "em_session_id"
                        ],

                        clarity_score=report_data.get(
                            "clarity_score",
                            5,
                        ),

                        transcript=transcript,

                    )

                    # ==========================================
                    # LOG WEAK SUBTOPIC
                    # ==========================================

                    weak_topic = report_data.get(
                        "weak_subtopic"
                    )

                    if weak_topic:

                        misconceptions.log_concept_weakness(

                            student_id=st.session_state[
                                "em_student_id"
                            ],

                            topic=topic,

                            sub_concept=weak_topic,

                            clarity_score=report_data.get(
                                "clarity_score",
                                5,
                            ),

                        )

                st.rerun()
    # ======================================================
    # DIAGNOSTIC REPORT
    # ======================================================

    if report is not None:

        st.divider()

        render_page_header(
            title="Diagnostic Report",
            subtitle="Here's how you performed during this teaching session.",
            icon="📊",
        )

        score = report.get("clarity_score", 5)

        if score >= 7:
            label = "Strong Understanding"
        elif score >= 4:
            label = "Partial Understanding"
        else:
            label = "Needs Improvement"

        left, right = st.columns([1, 2], gap="large")

        # --------------------------------------------------
        # SCORE
        # --------------------------------------------------

        with left:

            render_score_badge(
                score,
                label,
            )

            calibration_result = (
                calibration.compute_calibration_gap(
                    confidence,
                    score,
                )
            )

            st.write("")

            render_metric_card(
                "Self Rating",
                f"{confidence}/10",
            )

            render_metric_card(
                "AI Score",
                f"{score}/10",
            )

            render_info_card(
                "Calibration",
                calibration_result["label"].replace(
                    "-",
                    " ",
                ).title(),
                "info",
            )

        # --------------------------------------------------
        # DETAILS
        # --------------------------------------------------

        with right:

            correct = report.get(
                "correct_points",
                [],
            )

            if correct:

                st.subheader("✅ Strengths")

                for point in correct:

                    st.markdown(
                        f"- {point}"
                    )

            misconception = report.get(
                "misconception_found"
            )

            correction = report.get(
                "correct_explanation"
            )

            if misconception:

                st.write("")

                render_misconception_block(
                    misconception,
                    correction,
                )

            weak = report.get(
                "weak_subtopic"
            )

            if weak:

                render_info_card(
                    "🎯 Weakest Sub-topic",
                    weak,
                    "warning",
                )

        st.divider()

        c1, c2 = st.columns(2)

        with c1:

            if st.button(
                "🔄 Try Again",
                use_container_width=True,
            ):

                reset_session()

                st.rerun()

        with c2:

            if st.button(
                "🏠 Back to Home",
                use_container_width=True,
            ):

                reset_session()

                st.switch_page("app.py")

    # ======================================================
    # FOOTER
    # ======================================================

    st.divider()

    render_footer()
