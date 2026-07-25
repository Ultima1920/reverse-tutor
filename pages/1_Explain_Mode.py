import streamlit as st
from core.ai_engine import get_peer_reply
from core.persona import get_system_prompt
from core.misconceptions import get_misconceptions_for_topic
from core.voice import transcribe_audio, speak_reply

st.set_page_config(page_title="Explain Mode", page_icon="🗣️")

st.title("🗣️ Explain Mode")
st.write("Teach a topic to your confused peer!")

# Session state initialization
if "messages" not in st.session_state:
    st.session_state.messages = []
if "topic" not in st.session_state:
    st.session_state.topic = "Photosynthesis" # Default topic
if "enable_tts" not in st.session_state:
    st.session_state.enable_tts = False

# Sidebar settings
st.sidebar.header("Session Settings")
st.session_state.topic = st.sidebar.selectbox(
    "Select Topic to Teach",
    ["Photosynthesis", "Fractions", "Gravity", "Custom"]
)
if st.session_state.topic == "Custom":
    st.session_state.topic = st.sidebar.text_input("Enter custom topic:")

st.session_state.enable_tts = st.sidebar.checkbox("🔊 Hear the response (Text-to-Speech)", value=st.session_state.enable_tts)

if st.sidebar.button("Clear Conversation"):
    st.session_state.messages = []
    st.rerun()

# Display chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# --- UI Flow as per PDF ---

# 1. Capture Audio
st.write("---")
st.subheader("Your Explanation")
audio_value = st.audio_input("Explain the concept (Voice)")

# Transcription logic
transcribed_text = ""
if audio_value is not None:
    # We only want to transcribe once per audio recording to avoid unnecessary API calls
    # Streamlit re-runs on every interaction, so we need to be careful.
    # In a real app, we'd hash the audio to check if it's new, but for this demo, 
    # we'll transcribe and store it in session state if it changes.
    
    if "last_audio" not in st.session_state or st.session_state.last_audio != audio_value:
        with st.spinner("Transcribing..."):
            transcribed_text = transcribe_audio(audio_value) or ""
            st.session_state.last_audio = audio_value
            st.session_state.transcribed_text = transcribed_text
    else:
        transcribed_text = st.session_state.get("transcribed_text", "")

# 3 & 4. Text Input (Fallback and Confirmation)
# The user can edit the transcription or just type directly.
user_input = st.text_area(
    "Edit your transcribed explanation or type it here:", 
    value=transcribed_text,
    height=100
)

# Process the explanation
if st.button("Send Explanation"):
    if user_input.strip() == "":
        st.warning("Please provide an explanation before sending.")
    else:
        # Add user message to state
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        # Display user message immediately (optional, it will show on rerun anyway)
        with st.chat_message("user"):
            st.write(user_input)
            
        with st.spinner("Peer is thinking..."):
            # Get Context (Misconceptions)
            misconceptions = get_misconceptions_for_topic(st.session_state.topic)
            sys_prompt = get_system_prompt(st.session_state.topic, misconceptions)
            
            # Call AI
            reply_data = get_peer_reply(sys_prompt, st.session_state.messages)
            
            ai_reply = reply_data.get("peer_reply", "I'm not sure what to say.")
            internal_gap = reply_data.get("internal_gap_flag", True)
            
            # Add AI response to state
            st.session_state.messages.append({"role": "assistant", "content": ai_reply})
            
            # 5. Optional TTS
            if st.session_state.enable_tts:
                speak_reply(ai_reply)
        
        st.rerun()

# Display internal state for debug/demo purposes
with st.expander("Show AI Internal State"):
    if st.session_state.messages and st.session_state.messages[-1]["role"] == "assistant":
        # We don't store the exact flag in the message list for simplicity, but we can infer it
        # from the last reply if we wanted. For now, just show it's active.
        st.write("AI is active. It uses its system prompt to determine if it still has a gap.")
    else:
        st.write("No AI responses yet.")
