"""
pages/2_Error_Hunt_Mode.py — Error Hunt Mode for Reverse Tutor AI.
 
The AI generates a 3-5 sentence explanation of a topic with exactly one
planted factual error. The student reads it and guesses what's wrong.
The AI then reveals whether they found the real error, what it was, and the
correct version of the fact.
"""
 
import streamlit as st
from dotenv import load_dotenv
 
load_dotenv()
 
st.set_page_config(
    page_title="Error Hunt Mode — Reverse Tutor AI",
    page_icon="🔍",
    layout="wide",
)
 
from core import ai_engine
 
# ---------------------------------------------------------------------------
# Session state defaults
# ---------------------------------------------------------------------------
 
if "eh_topic" not in st.session_state:
    st.session_state["eh_topic"] = ""
if "eh_explanation" not in st.session_state:
    st.session_state["eh_explanation"] = None
if "eh_result" not in st.session_state:
    st.session_state["eh_result"] = None
if "eh_guess" not in st.session_state:
    st.session_state["eh_guess"] = ""
 
# ---------------------------------------------------------------------------
# Page header
# ---------------------------------------------------------------------------
st.title("🔍 Error Hunt Mode")
st.markdown(
    "The AI writes a **subtly wrong explanation** with one planted factual error. "
    "Your job: spot the mistake. Great for sharpening critical thinking."
)
st.divider()
 
# ---------------------------------------------------------------------------
# Topic input — any subject, not limited to a preset list
# ---------------------------------------------------------------------------
col_left, col_right = st.columns([2, 1])
 
with col_left:
    selected_topic = st.text_input(
        "📖 What topic should Alex write about?",
        value=st.session_state["eh_topic"],
        placeholder="e.g. Photosynthesis, the French Revolution, Big-O notation, offside rule in football…",
        key="eh_topic_input",
    ).strip()
 
    # If topic changed, clear the old explanation
    if selected_topic != st.session_state["eh_topic"]:
        st.session_state["eh_topic"] = selected_topic
        st.session_state["eh_explanation"] = None
        st.session_state["eh_result"] = None
        st.session_state["eh_guess"] = ""
 
    # Generate button
    if st.button("⚡ Generate a flawed explanation", type="primary", key="eh_generate"):
        if not selected_topic:
            st.error("Please enter a topic before generating an explanation.")
        else:
            with st.spinner("Generating a flawed explanation…"):
                explanation = ai_engine.generate_flawed_explanation(selected_topic)
            st.session_state["eh_explanation"] = explanation
            st.session_state["eh_result"] = None
            st.session_state["eh_guess"] = ""
            st.rerun()
 
with col_right:
    st.info(
        "**Tips for error hunting:**\n\n"
        "- Read every sentence carefully\n"
        "- Think about the facts you're sure of\n"
        "- The error sounds plausible but is factually wrong\n"
        "- It won't be a typo or grammar mistake"
    )
 
# ---------------------------------------------------------------------------
# Show the flawed explanation (if generated)
# ---------------------------------------------------------------------------
if st.session_state["eh_explanation"]:
    st.divider()
    st.subheader(f"📝 Explanation: {st.session_state['eh_topic']}")
    st.markdown(
        f"> {st.session_state['eh_explanation']}",
    )
 
    # Only show the guess input if we haven't revealed yet
    if st.session_state["eh_result"] is None:
        st.divider()
        guess = st.text_area(
            "🎯 What do you think is wrong with this explanation?",
            value=st.session_state["eh_guess"],
            height=100,
            placeholder="Describe the error you spotted…",
            key="eh_guess_input",
        )
        st.session_state["eh_guess"] = guess
 
        if st.button("🔎 Reveal the answer", type="primary", key="eh_reveal"):
            if not guess.strip():
                st.warning("Please enter your guess before revealing.")
            else:
                with st.spinner("Evaluating your guess…"):
                    result = ai_engine.reveal_error_hunt_result(
                        flawed_explanation=st.session_state["eh_explanation"],
                        student_guess=guess.strip(),
                    )
                st.session_state["eh_result"] = result
                st.rerun()
 
# ---------------------------------------------------------------------------
# Show the result card (if revealed)
# ---------------------------------------------------------------------------
if st.session_state["eh_result"] is not None:
    result = st.session_state["eh_result"]
    st.divider()
    st.subheader("📊 Result")
 
    if result.get("correct"):
        st.success("🎉 **Correct!** You found the real error!")
    else:
        st.error("❌ **Not quite.** That wasn't the main planted error.")
 
    col_err, col_fix = st.columns(2)
 
    with col_err:
        st.markdown("**🔴 The actual planted error:**")
        st.error(result.get("actual_error", "Unknown"))
 
    with col_fix:
        st.markdown("**✅ The correct explanation:**")
        st.success(result.get("explanation", "Unknown"))
 
    st.divider()
    if st.button("🔄 Try another topic", key="eh_reset"):
        st.session_state["eh_explanation"] = None
        st.session_state["eh_result"] = None
        st.session_state["eh_guess"] = ""
        st.rerun()
 
