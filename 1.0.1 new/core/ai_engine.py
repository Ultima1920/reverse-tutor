import google.generativeai as genai
import os
import time
import json
from dotenv import load_dotenv
from core.memory import format_history

# Load environment variables from .env if present
load_dotenv()

# Configure Gemini with API key from environment
api_key = os.environ.get("GEMINI_API_KEY", "")
if api_key:
    genai.configure(api_key=api_key)

# Initialize the Gemini model, requesting JSON output
# Using gemini-1.5-flash for free-tier reliability
MODEL_NAME = "gemini-1.5-flash"

def _get_model():
    """Returns a configured Gemini model. Re-checks API key on each call so
    the user can set the key at runtime without restarting."""
    key = os.environ.get("GEMINI_API_KEY", "")
    if key:
        genai.configure(api_key=key)
    return genai.GenerativeModel(
        MODEL_NAME,
        generation_config={"response_mime_type": "application/json"}
    )

def _call_gemini(prompt: str, retries: int = 3) -> str | None:
    """
    Internal helper: calls Gemini with exponential backoff on 429 errors.
    Returns raw response text or None on failure.
    """
    if not os.environ.get("GEMINI_API_KEY"):
        return None

    model = _get_model()
    for attempt in range(retries + 1):
        try:
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            error_str = str(e)
            if "429" in error_str and attempt < retries:
                wait = 2 ** attempt  # exponential backoff: 1s, 2s, 4s
                time.sleep(wait)
                continue
            print(f"Gemini API error on attempt {attempt}: {e}")
            return None
    return None


def get_peer_reply(system_prompt: str, conversation_history: list, retries: int = 3) -> dict:
    """
    Sends the confused-peer system prompt + conversation so far to Gemini.
    Returns {"peer_reply": str, "internal_gap_flag": bool}.
    Handles free-tier rate limits gracefully using exponential backoff.
    """
    if not os.environ.get("GEMINI_API_KEY"):
        return {
            "peer_reply": "⚠️ GEMINI_API_KEY is not set. Please add it to your .env file to use the AI features.",
            "internal_gap_flag": True
        }

    full_prompt = system_prompt + "\n\n" + format_history(conversation_history)
    raw = _call_gemini(full_prompt, retries)

    if raw is None:
        return {
            "peer_reply": "Sorry, I couldn't connect to the AI right now. Please try again in a moment.",
            "internal_gap_flag": True
        }

    try:
        data = json.loads(raw)
        if "peer_reply" not in data:
            data["peer_reply"] = str(data)
        if "internal_gap_flag" not in data:
            data["internal_gap_flag"] = True
        return data
    except json.JSONDecodeError:
        return {
            "peer_reply": "Hmm, I'm having trouble organizing my thoughts right now...",
            "internal_gap_flag": True
        }


def get_diagnostic_report(topic: str, conversation_history: list) -> dict:
    """
    Switches the AI out of confused-peer mode and asks it to evaluate
    how well the student explained the topic.
    Returns:
    {
        "clarity_score": int (1-10),
        "correct_points": [str],
        "misconception_found": str | null,
        "correct_explanation": str | null,
        "weak_subtopic": str | null
    }
    """
    _FALLBACK = {
        "clarity_score": 5,
        "correct_points": ["Unable to generate report — API error."],
        "misconception_found": None,
        "correct_explanation": None,
        "weak_subtopic": None
    }

    if not os.environ.get("GEMINI_API_KEY"):
        _FALLBACK["correct_points"] = ["⚠️ GEMINI_API_KEY not set — cannot generate report."]
        return _FALLBACK

    history_text = format_history(conversation_history)
    prompt = f"""You are now an expert educator evaluating a student's explanation of "{topic}".
Read the conversation below and score the student's understanding.

{history_text}

Return a JSON object with exactly these keys:
- "clarity_score": integer 1-10 rating how clearly the student explained the topic
- "correct_points": array of short strings (2-4 items) listing what the student got right
- "misconception_found": string describing any major misconception the student revealed, or null if none
- "correct_explanation": string giving the correct explanation for any misconception found, or null if misconception_found is null
- "weak_subtopic": a short (1-5 word) label for the weakest subtopic the student struggled with, or null if they were strong throughout

Be concise, fair, and encouraging. Focus on what the student said, not on the AI's questions.
"""

    raw = _call_gemini(prompt)

    if raw is None:
        return _FALLBACK

    try:
        data = json.loads(raw)
        # Ensure all required keys are present
        data.setdefault("clarity_score", 5)
        data.setdefault("correct_points", [])
        data.setdefault("misconception_found", None)
        data.setdefault("correct_explanation", None)
        data.setdefault("weak_subtopic", None)
        # Clamp clarity_score to valid range
        data["clarity_score"] = max(1, min(10, int(data["clarity_score"])))
        return data
    except (json.JSONDecodeError, ValueError, TypeError):
        return _FALLBACK


def generate_flawed_explanation(topic: str) -> dict:
    """
    Generates a 3-5 sentence explanation of the topic that contains exactly
    one planted factual error. Does NOT reveal which sentence contains the error.
    Returns:
    {
        "explanation": str,
        "actual_error": str,
        "actual_explanation": str
    }
    """
    _FALLBACK = {
        "explanation": f"Unable to generate a flawed explanation for {topic}. Please check your API key and try again.",
        "actual_error": "N/A",
        "actual_explanation": "N/A"
    }

    if not os.environ.get("GEMINI_API_KEY"):
        _FALLBACK["explanation"] = "⚠️ GEMINI_API_KEY not set."
        return _FALLBACK

    prompt = f"""You are creating a study challenge about "{topic}".

Write a 3-5 sentence explanation of "{topic}" that sounds plausible and mostly correct, but contains EXACTLY ONE deliberate factual error.

Return a JSON object with these keys:
- "explanation": the full 3-5 sentence explanation (do NOT hint at which sentence has the error)
- "actual_error": a single sentence describing what the factual error is
- "actual_explanation": the correct version of that fact

The error should be subtle enough that a student who partially understands the topic might miss it.
"""

    raw = _call_gemini(prompt)
    if raw is None:
        return _FALLBACK

    try:
        data = json.loads(raw)
        data.setdefault("explanation", _FALLBACK["explanation"])
        data.setdefault("actual_error", "Unknown error")
        data.setdefault("actual_explanation", "Unknown correction")
        return data
    except (json.JSONDecodeError, ValueError):
        return _FALLBACK


def reveal_error_hunt_result(flawed_explanation: str, actual_error: str, actual_explanation: str, student_guess: str) -> dict:
    """
    Evaluates whether the student correctly identified the planted factual error.
    Returns:
    {
        "correct": bool,
        "actual_error": str,
        "explanation": str,
        "feedback": str
    }
    """
    _FALLBACK = {
        "correct": False,
        "actual_error": actual_error,
        "explanation": actual_explanation,
        "feedback": "Could not evaluate your answer — please check your API key."
    }

    if not os.environ.get("GEMINI_API_KEY"):
        _FALLBACK["feedback"] = "⚠️ GEMINI_API_KEY not set."
        return _FALLBACK

    prompt = f"""A student was given this explanation with one planted factual error:

EXPLANATION:
{flawed_explanation}

THE ACTUAL PLANTED ERROR:
{actual_error}

THE STUDENT'S GUESS AT THE ERROR:
{student_guess}

Decide if the student's guess correctly identifies the same factual error (they don't need to use exact words, just the right concept).

Return a JSON object with these keys:
- "correct": boolean — true if the student identified the correct error concept, false otherwise
- "actual_error": the actual error (copy it verbatim from above)
- "explanation": the correct explanation (use: "{actual_explanation}")
- "feedback": a 1-2 sentence encouraging comment to the student about their answer
"""

    raw = _call_gemini(prompt)
    if raw is None:
        return _FALLBACK

    try:
        data = json.loads(raw)
        data.setdefault("correct", False)
        data.setdefault("actual_error", actual_error)
        data.setdefault("explanation", actual_explanation)
        data.setdefault("feedback", "Good effort!")
        return data
    except (json.JSONDecodeError, ValueError):
        return _FALLBACK
