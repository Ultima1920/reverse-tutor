# 🎓 Reverse Tutor AI

> *"The best way to learn is to teach."* — Richard Feynman

## What Is This?

**Reverse Tutor AI** flips the traditional tutoring model on its head. Instead of an AI explaining concepts *to* you, *you* explain the concept *to* the AI — which role-plays as a curious, slightly confused peer student. The AI asks pointed follow-up questions that deliberately expose the gaps, assumptions, and misconceptions in your explanation. After a short conversation, it produces a diagnostic report scoring your understanding and pinpointing exactly where your mental model broke down.

This is a direct implementation of the **Feynman Technique**: if you can't explain it simply, you don't understand it well enough. This app makes that test rigorous, repeatable, and data-driven.

**Built for hackathon judges**: All AI runs on the Google Gemini free tier — no credit card, no paid services anywhere in the stack.

---

## Modes

| Mode | Description |
|------|-------------|
| 🗣️ **Explain Mode** | You explain, the AI probes. Core Feynman experience. |
| 🔍 **Error Hunt Mode** | AI generates a subtly wrong explanation; you find the planted error. |
| 📊 **Dashboard** | Track your clarity scores over time and see your calibration gap. |
| 📚 **Misconception Library** | Browse common misconceptions seeded by topic. |

---

## Setup

### 1. Clone & create a virtual environment
```bash
git clone <your-repo-url>
cd reverse-tutor
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

> **Note on PyAudio (Windows)**: PyAudio may fail to install via pip on Windows without a C compiler. If it fails, voice input will be automatically disabled and you can still use the keyboard input mode. You can also install a pre-built wheel from https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio

### 3. Get a free Gemini API key
1. Go to [Google AI Studio](https://aistudio.google.com) — no credit card required
2. Click **Get API Key** → **Create API key**
3. Copy the key

### 4. Configure the environment
```bash
cp .env.example .env
# Edit .env and paste your key:
# GEMINI_API_KEY=AIza...
```

### 5. Run the app
```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`.

---

## Architecture

```
reverse-tutor/
├── app.py                    # Streamlit entry point
├── core/
│   ├── db.py                 # SQLite schema + helper functions
│   ├── ai_engine.py          # Gemini API calls (peer reply, diagnostics)
│   ├── persona.py            # System prompt builder for confused-peer role
│   ├── memory.py             # Conversation history formatter
│   ├── misconceptions.py     # Misconception DB wrappers
│   ├── calibration.py        # Difficulty adjustment + calibration gap
│   └── voice.py              # Offline STT (SpeechRecognition) + TTS (pyttsx3)
└── pages/
    ├── 1_Explain_Mode.py
    ├── 2_Error_Hunt_Mode.py
    ├── 3_Dashboard.py
    └── 4_Misconception_Library.py
```

---

## Free Services Used

| Component | Service | Cost |
|-----------|---------|------|
| AI / LLM | Google Gemini free tier (`gemini-3.1-flash-lite`) | Free |
| Database | SQLite (local file) | Free |
| Speech-to-Text | `SpeechRecognition` (Google Web Speech API, free for light use) | Free |
| Text-to-Speech | `pyttsx3` (offline, system TTS) | Free |
