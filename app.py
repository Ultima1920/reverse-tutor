import streamlit as st
from core.db import init_db
import os
from dotenv import load_dotenv

# Load env variables
load_dotenv()

st.set_page_config(
    page_title="Reverse Tutor AI",
    page_icon="🎓",
    layout="wide"
)

# Initialize DB on first load
if 'db_initialized' not in st.session_state:
    init_db()
    st.session_state.db_initialized = True

st.title("Reverse Tutor AI 🎓")

# Display a warning if API key is missing
if not os.environ.get("GEMINI_API_KEY"):
    st.warning("⚠️ GEMINI_API_KEY is not set. The AI features will not work until you configure it in your environment or `.env` file.")

st.markdown("""
Welcome to the **Reverse Tutor AI**!

In this app, *you* are the teacher. Select a mode from the sidebar to begin. 
The AI plays the role of a confused peer who might have some common misconceptions about the topic.
Your goal is to explain the concepts clearly enough that your "peer" finally understands!

### Modes available:
*   **Explain Mode**: The core experience. Try to teach a topic to the AI.
*   **Error Hunt Mode**: Analyze AI mistakes (Scaffolding).
*   **Dashboard**: View your teaching progress (Scaffolding).
*   **Misconception Library**: Browse known misconceptions (Scaffolding).
""")

st.sidebar.success("Select a mode from the menu above.")
