"""
core/voice.py — Offline voice input/output for Reverse Tutor AI.

Speech-to-Text: SpeechRecognition library using Google Web Speech API
    (free for light use, no API key required).
Text-to-Speech: pyttsx3 (uses the OS built-in TTS engine — fully offline).

Both functions are wrapped in try/except so that:
- A missing microphone never crashes the app
- A TTS engine failure silently no-ops
- A missing PyAudio installation is handled gracefully

Voice is an OPTIONAL enhancement. The app must still work without it.
"""

import logging

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Speech-to-Text
# ---------------------------------------------------------------------------

def transcribe_audio(audio_bytes: bytes) -> str | None:
    """Convert raw audio bytes to text using SpeechRecognition.

    Uses the Google Web Speech API (free tier, no key needed for light use).
    Returns None if transcription fails for any reason — callers should
    fall back to text input rather than raising an error to the user.

    Args:
        audio_bytes: Raw audio data (WAV format preferred).

    Returns:
        Transcribed text string, or None on any failure.
    """
    try:
        import speech_recognition as sr  # type: ignore
        import io

        recognizer = sr.Recognizer()

        # Wrap raw bytes in a file-like object for AudioFile
        audio_file = io.BytesIO(audio_bytes)
        with sr.AudioFile(audio_file) as source:
            audio_data = recognizer.record(source)

        text = recognizer.recognize_google(audio_data)
        return text.strip() if text else None

    except ImportError:
        logger.warning("SpeechRecognition not installed — voice input unavailable.")
        return None
    except Exception as exc:
        # Covers sr.UnknownValueError, sr.RequestError, and any IO issues
        logger.warning("Transcription failed: %s", exc)
        return None


# ---------------------------------------------------------------------------
# Text-to-Speech
# ---------------------------------------------------------------------------

def speak_reply(text: str, rate: int = 175) -> None:
    """Speak the given text aloud using pyttsx3 (offline TTS).

    Creates a fresh engine instance per call to avoid state issues in the
    Streamlit re-run model. Silently no-ops if pyttsx3 is not installed or
    if the TTS engine fails — a TTS failure should never crash the app.

    Args:
        text: The text to speak.
        rate: Speech rate in words per minute (default 175, ~natural pace).
    """
    try:
        import pyttsx3  # type: ignore

        engine = pyttsx3.init()
        engine.setProperty("rate", rate)
        engine.say(text)
        engine.runAndWait()
        engine.stop()

    except ImportError:
        logger.warning("pyttsx3 not installed — TTS unavailable.")
    except Exception as exc:
        # RuntimeError, OSError, etc. — never propagate to the UI
        logger.warning("TTS failed: %s", exc)
