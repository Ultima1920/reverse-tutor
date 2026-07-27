import streamlit as st
from core.ai_engine import get_peer_reply, get_diagnostic_report
from core.persona import get_system_prompt
from core.misconceptions import get_misconceptions_for_topic, log_concept_weakness
from core.calibration import adjust_difficulty, compute_calibration_gap
from core.voice import transcribe_audio, speak_reply
from core.db import create_session, update_session_result

st.set_page_config(page_title="Explain Mode — Reverse Tutor AI", page_icon="🗣️", layout="wide")

# ── CSS Tweaks ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
.report-card {
    background: linear-gradient(135deg, #1e1e2e, #2a2a3e);
    border-radius: 16px;
    padding: 24px;
    margin-top: 16px;
    border: 1px solid #3a3a5c;
}
.score-big {
    font-size: 3.5rem;
    font-weight: 900;
    text-align: center;
    line-height: 1;
}
.score-green { color: #4ade80; }
.score-yellow { color: #facc15; }
.score-red { color: #f87171; }
.label-chip {
    display: inline-block;
    padding: 4px 12px;
    border-radius: 999px;
    font-size: 0.8rem;
    font-weight: 600;
    margin-top: 4px;
}
.chip-over { background: #7f1d1d; color: #fca5a5; }
.chip-under { background: #1e3a5f; color: #93c5fd; }
.chip-well  { background: #14532d; color: #86efac; }
</style>
""", unsafe_allow_html=True)

TOPICS = ["Photosynthesis", "Fractions", "Gravity", "Custom…"]

# ── Session State Defaults ────────────────────────────────────────────────────
def _init_state():
    defaults = {
        "em_messages": [],           # chat history
        "em_gap_history": [],        # list of bool (internal_gap_flag per turn)
        "em_session_id": None,
        "em_topic": TOPICS[0],
        "em_confidence": 5,
        "em_started": False,
        "em_report": None,           # diagnostic report dict when generated
        "em_system_prompt": "",
        "em_tts_enabled": False,
        "em_input_mode": "Text",
        "em_last_audio": None,
        "em_transcribed": "",
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

_init_state()

# Handle pre-fill from Dashboard "Re-probe" button
if "prefill_topic" in st.session_state and st.session_state.prefill_topic:
    st.session_state.em_topic = st.session_state.prefill_topic
    st.session_state.prefill_topic = None

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("⚙️ Session Settings")

    topic_choice = st.selectbox(
        "📚 Topic to Teach",
        TOPICS,
        index=TOPICS.index(st.session_state.em_topic) if st.session_state.em_topic in TOPICS else 0,
        disabled=st.session_state.em_started
    )
    if topic_choice == "Custom…":
        custom = st.text_input("Enter your topic:", disabled=st.session_state.em_started)
        topic = custom.strip() if custom else "General"
    else:
        topic = topic_choice
    st.session_state.em_topic = topic

    confidence = st.slider(
        "🎯 How well do you understand this? (1–10)",
        1, 10,
        value=st.session_state.em_confidence,
        help="Be honest! We'll compare this to your actual score at the end.",
        disabled=st.session_state.em_started
    )
    st.session_state.em_confidence = confidence

    input_mode = st.radio(
        "🎤 Input Mode",
        ["Text", "Voice"],
        index=0 if st.session_state.em_input_mode == "Text" else 1,
        disabled=st.session_state.em_started
    )
    st.session_state.em_input_mode = input_mode

    st.session_state.em_tts_enabled = st.checkbox(
        "🔊 Speak AI responses (TTS)",
        value=st.session_state.em_tts_enabled
    )

    if st.session_state.em_started:
        if st.button("🔄 Reset Session"):
            for k in list(st.session_state.keys()):
                if k.startswith("em_"):
                    del st.session_state[k]
            st.rerun()

# ── Main Area ─────────────────────────────────────────────────────────────────
st.title("🗣️ Explain Mode")
st.caption(f"Topic: **{st.session_state.em_topic}** · Self-confidence: **{st.session_state.em_confidence}/10**")

# ── Start Button ──────────────────────────────────────────────────────────────
if not st.session_state.em_started:
    st.info("👈 Configure your session in the sidebar, then click **Start Session** below.")
    if st.button("🚀 Start Session", type="primary", use_container_width=True):
        if not st.session_state.em_topic:
            st.error("Please enter a topic first.")
        else:
            # Build system prompt using misconceptions from DB
            misconceptions = get_misconceptions_for_topic(st.session_state.em_topic)
            difficulty = adjust_difficulty([])  # no history yet → standard
            sys_prompt = get_system_prompt(st.session_state.em_topic, misconceptions)
            st.session_state.em_system_prompt = sys_prompt

            # Create a DB session record
            session_id = create_session(
                student_id=1,
                topic=st.session_state.em_topic,
                mode="explain",
                self_rated_confidence=st.session_state.em_confidence
            )
            st.session_state.em_session_id = session_id
            st.session_state.em_started = True
            st.session_state.em_messages = []
            st.session_state.em_gap_history = []
            st.session_state.em_report = None
            st.rerun()

# ── Active Session ────────────────────────────────────────────────────────────
if st.session_state.em_started and not st.session_state.em_report:
    turn_count = len([m for m in st.session_state.em_messages if m["role"] == "user"])
    gaps = st.session_state.em_gap_history

    # Progress bar: 4 turns max (or until gap closes)
    progress = min(turn_count / 4, 1.0)
    st.progress(progress, text=f"Turn {turn_count}/4 — keep explaining!")

    # Render existing chat history
    for msg in st.session_state.em_messages:
        role_label = "🧑‍🎓 You" if msg["role"] == "user" else "🤔 Confused Peer"
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
            if msg["role"] == "assistant" and st.session_state.em_tts_enabled:
                if st.button("🔊 Hear it", key=f"tts_{msg.get('id',id(msg))}"):
                    speak_reply(msg["content"])

    # Check if we should auto-generate a report
    should_report = (turn_count >= 4) or (
        len(gaps) >= 2 and gaps[-1] is False and gaps[-2] is False
    )

    if should_report and turn_count > 0:
        with st.spinner("📊 Generating your diagnostic report…"):
            report = get_diagnostic_report(
                st.session_state.em_topic,
                st.session_state.em_messages
            )
            st.session_state.em_report = report

            # Build transcript string
            transcript_lines = [
                f"{m['role'].upper()}: {m['content']}"
                for m in st.session_state.em_messages
            ]
            transcript = "\n".join(transcript_lines)

            # Save to DB
            update_session_result(
                st.session_state.em_session_id,
                clarity_score=report["clarity_score"],
                transcript=transcript
            )

            # Log weakness if found
            if report.get("weak_subtopic"):
                log_concept_weakness(
                    student_id=1,
                    topic=st.session_state.em_topic,
                    sub_concept=report["weak_subtopic"],
                    clarity_score=report["clarity_score"]
                )
        st.rerun()

    elif not should_report:
        # ── Input area ────────────────────────────────────────────────────────
        st.divider()
        user_text = ""

        if st.session_state.em_input_mode == "Voice":
            st.write("**🎙️ Record your explanation:**")
            audio = st.audio_input("Speak now…", key="em_audio_widget")
            if audio is not None and audio != st.session_state.em_last_audio:
                st.session_state.em_last_audio = audio
                with st.spinner("🔄 Transcribing…"):
                    result = transcribe_audio(audio)
                if result:
                    st.session_state.em_transcribed = result
                    st.success(f"Transcribed: *{result}*")
                else:
                    st.warning("⚠️ Couldn't transcribe audio. Please type your explanation below.")
                    st.session_state.em_transcribed = ""

            user_text = st.text_area(
                "✏️ Edit transcription or type fallback:",
                value=st.session_state.em_transcribed,
                height=100,
                key="em_voice_fallback"
            )
        else:
            user_text = st.chat_input("Explain to your confused peer…")

        # Send the message
        if user_text and user_text.strip():
            # Add user message
            st.session_state.em_messages.append({"role": "user", "content": user_text.strip(), "id": len(st.session_state.em_messages)})

            # Adjust difficulty based on gap history
            difficulty = adjust_difficulty(st.session_state.em_gap_history)
            sys_prompt = get_system_prompt(st.session_state.em_topic, get_misconceptions_for_topic(st.session_state.em_topic))

            with st.spinner("🤔 Peer is thinking…"):
                reply_data = get_peer_reply(sys_prompt, st.session_state.em_messages)

            ai_reply = reply_data.get("peer_reply", "Hmm, I'm confused…")
            gap_flag = reply_data.get("internal_gap_flag", True)

            st.session_state.em_messages.append({"role": "assistant", "content": ai_reply, "id": len(st.session_state.em_messages)})
            st.session_state.em_gap_history.append(gap_flag)
            st.session_state.em_transcribed = ""  # clear for next turn

            if st.session_state.em_tts_enabled:
                speak_reply(ai_reply)

            st.rerun()

# ── Diagnostic Report Card ────────────────────────────────────────────────────
if st.session_state.em_report:
    report = st.session_state.em_report
    score = report["clarity_score"]
    cal = compute_calibration_gap(st.session_state.em_confidence, score)

    if score >= 7:
        score_cls = "score-green"
        score_emoji = "🟢"
    elif score >= 4:
        score_cls = "score-yellow"
        score_emoji = "🟡"
    else:
        score_cls = "score-red"
        score_emoji = "🔴"

    chip_map = {
        "overconfident": ("chip-over", "⬆️ Overconfident"),
        "underconfident": ("chip-under", "⬇️ Underconfident"),
        "well-calibrated": ("chip-well", "✅ Well-Calibrated"),
    }
    chip_cls, chip_label = chip_map.get(cal["label"], ("chip-well", cal["label"]))

    st.success("✅ Session complete! Here's your diagnostic report:")
    st.markdown('<div class="report-card">', unsafe_allow_html=True)

    col1, col2 = st.columns([1, 2])
    with col1:
        st.markdown(f'<div class="score-big {score_cls}">{score_emoji}<br>{score}<small style="font-size:1.2rem">/10</small></div>', unsafe_allow_html=True)
        st.markdown(f'<div style="text-align:center;margin-top:8px"><span class="label-chip {chip_cls}">{chip_label}</span></div>', unsafe_allow_html=True)
        gap_val = cal["gap"]
        st.caption(f"Self-rated: {st.session_state.em_confidence}/10 · Actual: {score}/10 · Gap: {'+' if gap_val > 0 else ''}{gap_val}")

    with col2:
        if report.get("correct_points"):
            st.subheader("✅ What you got right")
            for point in report["correct_points"]:
                st.markdown(f"- ✔️ {point}")

        if report.get("misconception_found"):
            st.subheader("⚠️ Misconception detected")
            st.error(f"**You said:** {report['misconception_found']}")
            if report.get("correct_explanation"):
                st.info(f"**Correct explanation:** {report['correct_explanation']}")

        if report.get("weak_subtopic"):
            st.subheader("📌 Weak subtopic logged")
            st.caption(f"We've noted **"{report['weak_subtopic']}"** as an area to revisit. Check the Dashboard!")

    st.markdown('</div>', unsafe_allow_html=True)

    if st.button("🔄 Start a New Session", type="primary"):
        for k in list(st.session_state.keys()):
            if k.startswith("em_"):
                del st.session_state[k]
        st.rerun()
