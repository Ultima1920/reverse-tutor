"""
core/voice.py
─────────────
Cloud-safe voice I/O for Reverse Tutor AI.

Why this module exists:
    The original design used `pyttsx3` (desktop text-to-speech) and
    `PyAudio` (live microphone streaming via `SpeechRecognition`).
    Both assume a local machine with real speakers/mic hardware attached
    to the same process that runs the code. On Streamlit Cloud, your
    Python code runs on a remote server with no speakers and no mic —
    the only mic/speakers that exist belong to the user's browser.

    This module keeps the exact same *features* (speak your explanation
    out loud, have the AI's response read back to you) but re-routes the
    audio through the browser correctly:

      - Input:  audio-recorder-streamlit (pure JS, records in-browser,
                sends the recorded bytes to Python) → no PyAudio, no
                portaudio, nothing to compile.
      - Output: gTTS (Google Text-to-Speech) renders an mp3 in memory →
                played back via st.audio in the user's browser.

    Nothing here touches the server's audio devices, so nothing can
    fail to install or fail to play.
"""

import io
import streamlit as st

# ── Optional imports guarded so the app NEVER crashes on missing/failed deps ──
try:
    from audio_recorder_streamlit import audio_recorder
    _RECORDER_AVAILABLE = True
except ImportError:
    _RECORDER_AVAILABLE = False

try:
    import speech_recognition as sr
    _SR_AVAILABLE = True
except ImportError:
    _SR_AVAILABLE = False

try:
    from gtts import gTTS
    _GTTS_AVAILABLE = True
except ImportError:
    _GTTS_AVAILABLE = False

VOICE_INPUT_ENABLED = _RECORDER_AVAILABLE and _SR_AVAILABLE
VOICE_OUTPUT_ENABLED = _GTTS_AVAILABLE


def voice_input_widget(key: str = "voice_input") -> str | None:
    """
    Renders a mic-recorder button in the browser. When the user finishes
    speaking, transcribes the recorded audio to text and returns it.

    Returns None if voice input isn't available or nothing was recorded.
    Always call this behind a check of VOICE_INPUT_ENABLED if you want
    to show a custom fallback message instead of the built-in warning.
    """
    if not VOICE_INPUT_ENABLED:
        st.info("🎙️ Voice input isn't available right now — you can type your answer instead.")
        return None

    audio_bytes = audio_recorder(
        text="Click to speak",
        icon_size="2x",
        key=key,
        pause_threshold=2.0,
    )

    if not audio_bytes:
        return None

    recognizer = sr.Recognizer()
    try:
        with sr.AudioFile(io.BytesIO(audio_bytes)) as source:
            audio_data = recognizer.record(source)
        transcript = recognizer.recognize_google(audio_data)
        return transcript
    except sr.UnknownValueError:
        st.warning("Couldn't quite catch that — please try speaking again, or type your answer.")
        return None
    except sr.RequestError:
        st.warning("Speech recognition service is temporarily unavailable — please type your answer instead.")
        return None
    except Exception:
        st.warning("Something went wrong processing the audio — please type your answer instead.")
        return None


def speak_text(text: str, key: str = "tts_audio", lang: str = "en", autoplay: bool = True) -> None:
    """
    Converts `text` to speech and renders an audio player in the browser.
    Silently shows a small note (never crashes) if TTS is unavailable.
    """
    if not text:
        return

    if not VOICE_OUTPUT_ENABLED:
        st.caption("🔇 Voice playback isn't available right now.")
        return

    try:
        mp3_buffer = io.BytesIO()
        gTTS(text=text, lang=lang).write_to_fp(mp3_buffer)
        mp3_buffer.seek(0)
        st.audio(mp3_buffer, format="audio/mp3", autoplay=autoplay)
    except Exception:
        st.caption("🔇 Couldn't generate audio for this response — showing text only.")
