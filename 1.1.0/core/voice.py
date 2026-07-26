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
import os
import io

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Audio format conversion helper
# ---------------------------------------------------------------------------

def _convert_to_wav(audio_bytes: bytes) -> bytes:
    """Convert audio bytes (webm, ogg, mp4, etc.) to standard WAV PCM format.

    Browser MediaRecorder (st.audio_input) typically produces audio/webm or
    audio/ogg data, whereas SpeechRecognition requires PCM WAV.
    """
    if not audio_bytes:
        return audio_bytes

    # 1. Try reading directly if it's already a valid WAV file
    try:
        import wave
        with wave.open(io.BytesIO(audio_bytes), "rb") as wf:
            if wf.getnchannels() > 0:
                return audio_bytes
    except Exception:
        pass

    # 2. Convert using pydub and imageio_ffmpeg
    try:
        import imageio_ffmpeg
        import pydub

        ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
        ffmpeg_dir = os.path.dirname(ffmpeg_exe)
        if ffmpeg_dir not in os.environ.get("PATH", ""):
            os.environ["PATH"] = os.environ.get("PATH", "") + os.path.pathsep + ffmpeg_dir

        pydub.AudioSegment.converter = ffmpeg_exe

        audio_segment = pydub.AudioSegment.from_file(io.BytesIO(audio_bytes))
        out_buf = io.BytesIO()
        audio_segment.export(out_buf, format="wav")
        return out_buf.getvalue()
    except Exception as exc:
        logger.warning("Audio conversion to WAV failed: %s", exc)
        return audio_bytes


# ---------------------------------------------------------------------------
# Speech-to-Text
# ---------------------------------------------------------------------------

def transcribe_audio(audio_bytes: bytes) -> str | None:
    """Convert audio bytes to text using SpeechRecognition.

    Uses the Google Web Speech API (free tier, no key needed for light use).
    Converts webm/ogg browser recordings to WAV automatically.

    Args:
        audio_bytes: Raw audio data (WAV, WEBM, OGG, etc.).

    Returns:
        Transcribed text string, or None on any failure.
    """
    if not audio_bytes:
        return None

    try:
        import speech_recognition as sr  # type: ignore

        # Convert webm/ogg browser recording to WAV PCM first
        wav_bytes = _convert_to_wav(audio_bytes)

        recognizer = sr.Recognizer()

        # Wrap WAV bytes in a file-like object for AudioFile
        audio_file = io.BytesIO(wav_bytes)
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
