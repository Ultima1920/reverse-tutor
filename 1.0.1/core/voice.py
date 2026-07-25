import speech_recognition as sr
import pyttsx3
import traceback

recognizer = sr.Recognizer()

# Initialize text-to-speech engine gracefully
try:
    tts_engine = pyttsx3.init()
except Exception as e:
    tts_engine = None
    print(f"Warning: Could not initialize pyttsx3 text-to-speech. TTS will be disabled. Error: {e}")

def transcribe_audio(audio_file) -> str | None:
    """
    Speech -> text. Called when student uses the mic input.
    audio_file can be the UploadedFile object returned by st.audio_input.
    Returns None if transcription fails, never crashes.
    """
    if audio_file is None:
        return None
        
    try:
        with sr.AudioFile(audio_file) as source:
            # Re-calibrate for ambient noise if needed, but for files it's usually fine
            audio = recognizer.record(source)
        try:
            return recognizer.recognize_google(audio)
        except sr.UnknownValueError:
            # Audio was not understandable
            return None
        except sr.RequestError as e:
            # API unreachable or rate limited
            print(f"Could not request results from Google Speech Recognition service; {e}")
            return None
    except Exception as e:
        print(f"Unexpected error processing audio file:\n{traceback.format_exc()}")
        return None

def speak_reply(text: str) -> None:
    """
    Text -> speech. Optional: makes the confused peer 'talk'.
    Fails silently if TTS is not available.
    """
    if tts_engine:
        try:
            tts_engine.say(text)
            tts_engine.runAndWait()
        except Exception as e:
            print(f"Error during text-to-speech playback: {e}")
    else:
        print(f"TTS disabled. Would have said: {text}")
