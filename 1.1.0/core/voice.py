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

DEBUG NOTE: this version stores the last transcription error in a module
level variable so the calling page can display it in the UI. Once voice
input is confirmed working, you can strip out the _LAST_ERROR machinery.
"""
import io
import logging

logger = logging.getLogger(__name__)

# Holds a human-readable string describing the last transcription failure,
# so the Streamlit page can show it instead of a silent "couldn't transcribe".
_LAST_ERROR: str | None = None


def get_last_transcription_error() -> str | None:
    """Return details of the most recent transcribe_audio() failure, if any."""
    return _LAST_ERROR


# ---------------------------------------------------------------------------
# Speech-to-Text
# ---------------------------------------------------------------------------
def transcribe_audio(audio_bytes: bytes) -> str | None:
    """Convert raw audio bytes to text using SpeechRecognition.

    Returns None if transcription fails for any reason — callers should
    fall back to text input. Call get_last_transcription_error() right
    after a None return to see exactly what went wrong.
    """
    global _LAST_ERROR
    _LAST_ERROR = None

    if not audio_bytes:
        _LAST_ERROR = "No audio bytes were received from the recorder (audio_bytes was empty)."
        logger.warning(_LAST_ERROR)
        return None

    _LAST_ERROR = f"Received {len(audio_bytes)} bytes of audio; attempting to decode."
    logger.info(_LAST_ERROR)

    try:
        import speech_recognition as sr  # type: ignore
    except ImportError as exc:
        _LAST_ERROR = f"SpeechRecognition not installed: {exc}"
        logger.warning(_LAST_ERROR)
        return None

    recognizer = sr.Recognizer()

    # --- Attempt 1: standard AudioFile parsing (works for plain PCM WAV) ---
    try:
        audio_file = io.BytesIO(audio_bytes)
        with sr.AudioFile(audio_file) as source:
            audio_data = recognizer.record(source)
        text = recognizer.recognize_google(audio_data)
        if text:
            _LAST_ERROR = None
            return text.strip()
        _LAST_ERROR = "recognize_google returned an empty string (attempt 1)."
        return None
    except sr.UnknownValueError:
        _LAST_ERROR = "ATTEMPT 1 (AudioFile): Google could not understand the audio — likely silence, too short, or too quiet."
        logger.warning(_LAST_ERROR)
        # fall through to attempt 2 anyway, in case it's actually a decode issue
    except sr.RequestError as exc:
        _LAST_ERROR = f"ATTEMPT 1 (AudioFile): Could not reach Google's speech API — network/DNS/firewall issue: {exc}"
        logger.warning(_LAST_ERROR)
        return None  # no point retrying attempt 2, network is the problem
    except Exception as exc:
        _LAST_ERROR = f"ATTEMPT 1 (AudioFile) failed to parse the WAV file: {type(exc).__name__}: {exc}"
        logger.warning(_LAST_ERROR)
        # fall through to attempt 2

    # --- Attempt 2: robust decode via soundfile, bypassing wave/AudioFile ---
    try:
        import soundfile as sf  # type: ignore
    except ImportError as exc:
        _LAST_ERROR += f" | ATTEMPT 2: soundfile not installed, cannot retry: {exc}"
        logger.warning(_LAST_ERROR)
        return None

    try:
        data, samplerate = sf.read(io.BytesIO(audio_bytes), dtype="int16")

        if data.ndim > 1:
            data = data.mean(axis=1).astype("int16")

        raw_pcm = data.tobytes()
        audio_data = sr.AudioData(raw_pcm, samplerate, 2)

        text = recognizer.recognize_google(audio_data)
        if text:
            _LAST_ERROR = None
            return text.strip()
        _LAST_ERROR += " | ATTEMPT 2: recognize_google returned an empty string."
        return None

    except sr.UnknownValueError:
        _LAST_ERROR += " | ATTEMPT 2 (soundfile): Google could not understand the audio either."
        logger.warning(_LAST_ERROR)
        return None
    except sr.RequestError as exc:
        _LAST_ERROR += f" | ATTEMPT 2 (soundfile): Could not reach Google's speech API: {exc}"
        logger.warning(_LAST_ERROR)
        return None
    except Exception as exc:
        _LAST_ERROR += f" | ATTEMPT 2 (soundfile) also failed: {type(exc).__name__}: {exc}"
        logger.warning(_LAST_ERROR)
        return None


# ---------------------------------------------------------------------------
# Text-to-Speech
# ---------------------------------------------------------------------------
def speak_reply(text: str, rate: int = 175) -> None:
    """Speak the given text aloud using pyttsx3 (offline TTS)."""
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
        logger.warning("TTS failed: %s", exc)

