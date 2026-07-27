"""
pages/2_Error_Hunt_Mode.py
Reverse Tutor AI
"""

import streamlit as st
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="Error Hunt",
    page_icon="🔍",
    layout="wide",
)

# ==========================================================
# IMPORTS
# ==========================================================

from core.ui import (
    inject_base_css,
    render_page_header,
    render_metric_card,
    render_info_card,
    render_topic_chip,
    render_misconception_block,
    render_footer,
)

from core import ai_engine

inject_base_css()

# ==========================================================
# SESSION DEFAULTS
# ==========================================================

DEFAULTS = {

    "eh_topic": "",

    "eh_explanation": None,

    "eh_result": None,

    "eh_guess": "",

}

for key, value in DEFAULTS.items():

    if key not in st.session_state:

        st.session_state[key] = value

# ==========================================================
# HEADER
# ==========================================================

render_page_header(

    title="Error Hunt",

    subtitle=(
        "Read Alex's explanation carefully. "
        "Exactly one factual mistake has been planted. "
        "Can you find it?"
    ),

    icon="🔍",

)

render_info_card(

    "Challenge",

    """
Alex intentionally makes one subtle conceptual mistake.

Your goal is not to correct grammar or wording.

Find the single incorrect fact.
""",

    "warning",

)

st.divider()

# ==========================================================
# TOPIC SELECTION
# ==========================================================

left, right = st.columns(
    [2,1],
    gap="large",
)

with left:

    render_info_card(

        "Choose a Topic",

        "Enter any topic to generate a flawed explanation.",

        "success",

    )

    topic = st.text_input(

        "Topic",

        value=st.session_state["eh_topic"],

        placeholder="Binary Search, Photosynthesis, TCP/IP...",

    ).strip()

    if topic != st.session_state["eh_topic"]:

        st.session_state["eh_topic"] = topic

        st.session_state["eh_explanation"] = None

        st.session_state["eh_result"] = None

        st.session_state["eh_guess"] = ""

    st.write("")

    generate = st.button(

        "⚡ Generate Challenge",

        type="primary",

        use_container_width=True,

    )

    if generate:

        if not topic:

            st.error(
                "Please enter a topic."
            )

        else:

            with st.spinner(
                "Alex is preparing your challenge..."
            ):

                explanation = (
                    ai_engine.generate_flawed_explanation(
                        topic
                    )
                )

            st.session_state[
                "eh_explanation"
            ] = explanation

            st.session_state[
                "eh_result"
            ] = None

            st.session_state[
                "eh_guess"
            ] = ""

            st.rerun()

with right:

    render_info_card(

        "📋 Rules",

        """
• Exactly one mistake

• No grammar tricks

• Read every sentence

• Think conceptually

• Explain WHY it is wrong
""",

        "info",

    )

    render_info_card(

        "💡 Tip",

        """
If something feels slightly incorrect,
it probably is.

Question every fact.
""",

        "success",

    )

st.divider()
# ==========================================================
# EXPLANATION CARD
# ==========================================================

if st.session_state["eh_explanation"]:

    render_page_header(
        title="Find the Mistake",
        subtitle="Read carefully before making your guess.",
        icon="📄",
    )

    render_metric_card(
        "Current Topic",
        st.session_state["eh_topic"],
    )

    st.write("")

    render_info_card(
        "Alex's Explanation",
        st.session_state["eh_explanation"],
        "info",
    )

    st.divider()

    # ======================================================
    # GUESS SECTION
    # ======================================================

    if st.session_state["eh_result"] is None:

        render_page_header(
            title="Your Answer",
            subtitle="Explain which statement is incorrect and why.",
            icon="🎯",
        )

        guess = st.text_area(
            "What is the mistake?",
            value=st.session_state["eh_guess"],
            height=180,
            placeholder="""
Example:

The explanation says Binary Search works on unsorted arrays.

Binary Search actually requires the array to be sorted because...
""",
        )

        st.session_state["eh_guess"] = guess

        c1, c2 = st.columns([5, 1])

        with c2:

            reveal = st.button(
                "Reveal",
                type="primary",
                use_container_width=True,
            )

        if reveal:

            if not guess.strip():

                st.warning(
                    "Please enter your answer first."
                )

            else:

                with st.spinner(
                    "Checking your answer..."
                ):

                    result = (
                        ai_engine.reveal_error_hunt_result(
                            flawed_explanation=st.session_state[
                                "eh_explanation"
                            ],
                            student_guess=guess.strip(),
                        )
                    )

                st.session_state[
                    "eh_result"
                ] = result

                st.rerun()
# ==========================================================
# RESULT
# ==========================================================

if st.session_state["eh_result"] is not None:

    result = st.session_state["eh_result"]

    st.divider()

    render_page_header(
        title="Challenge Result",
        subtitle="Let's see how well you spotted the hidden mistake.",
        icon="📊",
    )

    score_col, detail_col = st.columns([1, 2], gap="large")

    # ------------------------------------------------------
    # LEFT PANEL
    # ------------------------------------------------------

    with score_col:

        if result.get("correct"):

            render_info_card(
                "🎉 Excellent!",
                "You correctly identified the planted misconception.",
                "success",
            )

            render_metric_card(
                "Result",
                "Correct ✅",
            )

        else:

            render_info_card(
                "❌ Not Quite",
                "Your answer didn't match the planted misconception.",
                "danger",
            )

            render_metric_card(
                "Result",
                "Incorrect",
            )

        render_metric_card(
            "Topic",
            st.session_state["eh_topic"],
        )

    # ------------------------------------------------------
    # RIGHT PANEL
    # ------------------------------------------------------

    with detail_col:

        st.subheader("📝 AI Feedback")

        render_misconception_block(

            misconception=result.get(
                "actual_error",
                "Unknown"
            ),

            correction=result.get(
                "explanation",
                "No explanation available."
            ),

        )

        if result.get("correct"):

            render_info_card(

                "Why this is good",

                """
You noticed the exact conceptual mistake.

This means you weren't simply reading —
you were actively verifying every statement.
""",

                "success",

            )

        else:

            render_info_card(

                "Learning Tip",

                """
Try reading each sentence independently.

Ask yourself:

• Is this always true?

• Would I teach this to someone else?

• Does this contradict something I already know?
""",

                "warning",

            )

    st.divider()

    # ======================================================
    # ACTION BUTTONS
    # ======================================================

    c1, c2 = st.columns(2)

    with c1:

        if st.button(
            "🔄 Try Another Topic",
            use_container_width=True,
        ):

            st.session_state["eh_explanation"] = None
            st.session_state["eh_result"] = None
            st.session_state["eh_guess"] = ""

            st.rerun()

    with c2:

        if st.button(
            "🏠 Back to Home",
            use_container_width=True,
        ):

            st.session_state["eh_explanation"] = None
            st.session_state["eh_result"] = None
            st.session_state["eh_guess"] = ""

            st.switch_page("app.py")

# ==========================================================
# FOOTER
# ==========================================================

st.divider()

render_footer()
