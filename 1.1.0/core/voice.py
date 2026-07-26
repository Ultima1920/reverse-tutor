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
import io
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
 
    Decoding strategy:
    1. Try SpeechRecognition's built-in AudioFile parser first (fast path,
       works when the browser sends plain 16-bit PCM WAV).
    2. If that fails — which happens often with st.audio_input, since
       browsers frequently encode float32 or "extensible" WAV headers that
       Python's stdlib `wave` module can't read — decode manually with
       `soundfile` (libsndfile-backed, handles virtually any WAV variant)
       and hand SpeechRecognition a manually-built AudioData object.
 
    Args:
        audio_bytes: Raw audio data (WAV format preferred).
 
    Returns:
        Transcribed text string, or None on any failure.
    """
    try:
        import speech_recognition as sr  # type: ignore
    except ImportError:
        logger.warning("SpeechRecognition not installed — voice input unavailable.")
        return None
 
    recognizer = sr.Recognizer()
 
    # --- Attempt 1: standard AudioFile parsing (works for plain PCM WAV) ---
    try:
        audio_file = io.BytesIO(audio_bytes)
        with sr.AudioFile(audio_file) as source:
            audio_data = recognizer.record(source)
        text = recognizer.recognize_google(audio_data)
        return text.strip() if text else None
    except sr.UnknownValueError:
        logger.warning("Google Web Speech API could not understand the audio.")
        return None
    except sr.RequestError as exc:
        logger.warning("Could not reach Google Web Speech API: %s", exc)
        return None
    except Exception as exc:
        # Most commonly a wave-format error (e.g. float32/extensible WAV
        # from the browser) — fall through to the soundfile-based decoder.
        logger.warning("Standard WAV parsing failed (%s) — retrying with soundfile.", exc)
 
    # --- Attempt 2: robust decode via soundfile, bypassing wave/AudioFile ---
    try:
        import soundfile as sf  # type: ignore
 
        data, samplerate = sf.read(io.BytesIO(audio_bytes), dtype="int16")
 
        # Downmix to mono if the capture came in as stereo
        if data.ndim > 1:
            data = data.mean(axis=1).astype("int16")
 
        raw_pcm = data.tobytes()
        audio_data = sr.AudioData(raw_pcm, samplerate, 2)  # sample_width=2 (int16)
 
        text = recognizer.recognize_google(audio_data)
        return text.strip() if text else None
 
    except ImportError:
        logger.warning("soundfile not installed — cannot recover from WAV parse failure.")
        return None
    except sr.UnknownValueError:
        logger.warning("Google Web Speech API could not understand the audio (soundfile path).")
        return None
    except sr.RequestError as exc:
        logger.warning("Could not reach Google Web Speech API (soundfile path): %s", exc)
        return None
    except Exception as exc:
        logger.warning("Transcription failed even after soundfile fallback: %s", exc)
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
 
