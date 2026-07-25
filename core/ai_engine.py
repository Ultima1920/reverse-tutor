import google.generativeai as genai
import os
import time
import json
from dotenv import load_dotenv
from core.memory import format_history

# Load environment variables from .env if present
load_dotenv()

# We configure here but typically Streamlit apps might pass secrets directly.
# Using os.environ gracefully handles local .env files.
api_key = os.environ.get("GEMINI_API_KEY", "")
if api_key:
    genai.configure(api_key=api_key)

# Initialize the Gemini model, requesting JSON output as per our persona prompt
model = genai.GenerativeModel(
    "gemini-1.5-flash",
    generation_config={"response_mime_type": "application/json"}
)

def get_peer_reply(system_prompt: str, conversation_history: list, retries: int = 2):
    """
    Sends the confused-peer system prompt + conversation so far to Gemini.
    Handles free-tier rate limits gracefully using exponential backoff.
    """
    if not os.environ.get("GEMINI_API_KEY"):
        return {"peer_reply": "Error: GEMINI_API_KEY is not set. Please configure your .env file.", "internal_gap_flag": True}

    full_prompt = system_prompt + "\n\n" + format_history(conversation_history)
    
    for attempt in range(retries + 1):
        try:
            response = model.generate_content(full_prompt)
            # Parse the JSON response
            try:
                data = json.loads(response.text)
                # Ensure the expected keys are present
                if "peer_reply" not in data:
                    data["peer_reply"] = str(data)
                if "internal_gap_flag" not in data:
                    data["internal_gap_flag"] = True
                return data
            except json.JSONDecodeError:
                # Fallback if the model didn't return valid JSON
                return {"peer_reply": "I'm having trouble organizing my thoughts... (Error parsing AI response)", "internal_gap_flag": True}
                
        except Exception as e:
            if "429" in str(e) and attempt < retries:
                time.sleep(2 ** attempt)  # simple exponential backoff
                continue
            print(f"Error calling Gemini API: {e}")
            return {"peer_reply": f"Sorry, my brain is fried right now... (API Error: {e})", "internal_gap_flag": True}
