import streamlit as st
from core.ai_engine import generate_flawed_explanation, reveal_error_hunt_result

st.set_page_config(page_title="Error Hunt Mode — Reverse Tutor AI", page_icon="🔍", layout="wide")

st.title("🔍 Error Hunt Mode")
st.caption("Read the explanation, find the one deliberate factual error, and prove you know your stuff!")

TOPICS = ["Photosynthesis", "Fractions", "Gravity"]

# ── Session state ─────────────────────────────────────────────────────────────
for k, v in {
    "eh_topic": TOPICS[0],
    "eh_flawed_data": None,    # dict: explanation, actual_error, actual_explanation
    "eh_guess": "",
    "eh_result": None,         # dict: correct, actual_error, explanation, feedback
}.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("⚙️ Settings")
    topic = st.selectbox("📚 Topic", TOPICS)
    st.session_state.eh_topic = topic

    if st.button("🔄 Reset"):
        for k in ["eh_flawed_data", "eh_guess", "eh_result"]:
            st.session_state[k] = None if k != "eh_guess" else ""
        st.rerun()

# ── Step 1: Generate flawed explanation ───────────────────────────────────────
st.subheader("Step 1 · Get a Flawed Explanation")

if st.session_state.eh_flawed_data is None:
    if st.button("⚡ Generate Flawed Explanation", type="primary", use_container_width=True):
        with st.spinner(f"Generating a tricky explanation about {st.session_state.eh_topic}…"):
            data = generate_flawed_explanation(st.session_state.eh_topic)
        st.session_state.eh_flawed_data = data
        st.session_state.eh_result = None
        st.session_state.eh_guess = ""
        st.rerun()
else:
    flawed_data = st.session_state.eh_flawed_data

    # Display the explanation in a styled box
    st.markdown(
        f"""<div style='background:#1e1e2e;border:1px solid #3a3a5c;border-radius:12px;padding:20px;
        font-size:1.05rem;line-height:1.7;'>{flawed_data['explanation']}</div>""",
        unsafe_allow_html=True
    )
    st.caption("☝️ One sentence above contains a deliberate factual error. Can you find it?")

    # ── Step 2: Student guess ─────────────────────────────────────────────────
    st.divider()
    st.subheader("Step 2 · Identify the Error")

    if st.session_state.eh_result is None:
        guess = st.text_area(
            "What do you think the error is? Describe it in your own words:",
            value=st.session_state.eh_guess,
            height=100,
            placeholder="e.g. 'The explanation says plants absorb oxygen, but they actually produce it…'"
        )
        st.session_state.eh_guess = guess

        if st.button("🔎 Reveal Answer", type="primary", disabled=not guess.strip()):
            with st.spinner("Evaluating your answer…"):
                result = reveal_error_hunt_result(
                    flawed_explanation=flawed_data["explanation"],
                    actual_error=flawed_data["actual_error"],
                    actual_explanation=flawed_data["actual_explanation"],
                    student_guess=guess
                )
            st.session_state.eh_result = result
            st.rerun()
    else:
        # ── Step 3: Display result ────────────────────────────────────────────
        result = st.session_state.eh_result
        st.divider()
        st.subheader("Step 3 · Results")

        if result.get("correct"):
            st.success("🎉 Correct! You spotted the error!")
        else:
            st.error("❌ Not quite — here's what the actual error was:")

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**🔴 The Planted Error**")
            st.info(result.get("actual_error", "N/A"))
        with col2:
            st.markdown("**✅ The Correct Fact**")
            st.success(result.get("explanation", "N/A"))

        st.markdown(f"**💬 Feedback:** {result.get('feedback', '')}")

        st.divider()
        if st.button("⚡ Try Another Explanation", use_container_width=True):
            st.session_state.eh_flawed_data = None
            st.session_state.eh_result = None
            st.session_state.eh_guess = ""
            st.rerun()
