import speech_recognition as sr
import pyttsx3

recognizer = sr.Recognizer()

try:
    tts_engine = pyttsx3.init()
except Exception as e:
    tts_engine = None
    print(f"Warning: Could not initialize pyttsx3 text-to-speech: {e}")

def transcribe_audio(audio_file) -> str:
    """
    Speech -> text. Called when student uses the mic input.
    audio_file can be the UploadedFile object returned by st.audio_input.
    """
    try:
        with sr.AudioFile(audio_file) as source:
            audio = recognizer.record(source)
        try:
            return recognizer.recognize_google(audio) # free, no key needed for basic use
        except sr.UnknownValueError:
            return None # signal the UI to fall back to text input
        except sr.RequestError as e:
            print(f"Could not request results from Google Speech Recognition service; {e}")
            return None
    except Exception as e:
        print(f"Error processing audio file: {e}")
        return None

def speak_reply(text: str):
    """
    Text -> speech. Optional: makes the confused peer 'talk'.
    """
    if tts_engine:
        try:
            tts_engine.say(text)
            tts_engine.runAndWait()
        except Exception as e:
            print(f"Error during text-to-speech: {e}")
    else:
        print(f"TTS disabled. Would have said: {text}")
