"""
core/ai_engine.py — All Google Gemini API interactions for Reverse Tutor AI.

Uses the google-generativeai SDK with JSON response mode for consistency.
Model: gemini-3.1-flash-lite (free tier, no credit card required).

Every function gracefully handles:
- Missing API key (returns safe fallback, no crash)
- 429 rate-limit errors (exponential backoff with retries)
- Malformed JSON from the model (returns a safe fallback dict)
"""

import os
import json
import time
import logging

from core.memory import format_history

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Gemini client setup
# ---------------------------------------------------------------------------

# We import google.generativeai lazily inside functions so that the app
# can still run (with degraded AI features) if the package isn't installed.

def _get_model(use_json_mode: bool = True):
    """Initialise and return a Gemini GenerativeModel instance.

    Returns None if the API key is missing or if the SDK can't be imported.
    """
    api_key = os.environ.get("GEMINI_API_KEY", "").strip()
    if not api_key:
        logger.warning("GEMINI_API_KEY is not set — AI features disabled.")
        return None

    try:
        import google.generativeai as genai  # type: ignore
        genai.configure(api_key=api_key)

        generation_config = {}
        if use_json_mode:
            generation_config["response_mime_type"] = "application/json"

        model = genai.GenerativeModel(
            model_name="gemini-3.1-flash-lite",
            generation_config=generation_config,
        )
        return model
    except Exception as exc:
        logger.error("Failed to create Gemini model: %s", exc)
        return None


def _call_with_retry(model, prompt: str, retries: int = 2) -> str | None:
    """Send a prompt to the model, retrying on rate-limit errors.

    Args:
        model: A GenerativeModel instance.
        prompt: The full prompt string (system + user content concatenated).
        retries: Number of additional attempts after the first failure.

    Returns:
        The model's text response, or None on persistent failure.
    """
    delay = 2  # seconds before first retry
    for attempt in range(retries + 1):
        try:
            response = model.generate_content(prompt)
            return response.text
        except Exception as exc:
            exc_str = str(exc)
            is_rate_limit = "429" in exc_str or "RESOURCE_EXHAUSTED" in exc_str.upper()

            if is_rate_limit and attempt < retries:
                wait = delay * (2 ** attempt)  # exponential backoff: 2s, 4s, …
                logger.warning("Rate limited. Retrying in %ds…", wait)
                time.sleep(wait)
            else:
                logger.error("Gemini call failed (attempt %d): %s", attempt + 1, exc)
                return None

    return None


def _parse_json_safe(raw: str | None, fallback: dict) -> dict:
    """Parse a JSON string, returning fallback on any error."""
    if raw is None:
        return fallback
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        logger.warning("Could not parse model JSON. Raw: %s", raw[:200])
        return fallback


# ---------------------------------------------------------------------------
# Peer reply (core explain-mode function)
# ---------------------------------------------------------------------------

def get_peer_reply(
    system_prompt: str,
    conversation_history: list[dict],
    retries: int = 2,
) -> dict:
    """Get the confused peer's next reply given the conversation so far.

    Args:
        system_prompt: The full persona system prompt (from core.persona).
        conversation_history: List of {"role": "user"|"assistant", "content": str}.
        retries: Max retry attempts on rate-limit errors.

    Returns:
        A dict with:
            - "peer_reply" (str): The peer's in-character response.
            - "internal_gap_flag" (bool): True if a gap still seems present.
    """
    _FALLBACK = {
        "peer_reply": (
            "Hmm, wait — I think I need a moment to process that. "
            "Can you try explaining that last bit again in different words?"
        ),
        "internal_gap_flag": True,
    }

    model = _get_model(use_json_mode=True)
    if model is None:
        return {
            "peer_reply": (
                "⚠️ AI is unavailable (API key missing or invalid). "
                "Please add your GEMINI_API_KEY to the .env file and restart."
            ),
            "internal_gap_flag": True,
        }

    # Build the full prompt: system instructions + transcript + latest student turn
    transcript = format_history(conversation_history)
    full_prompt = (
        f"{system_prompt}\n\n"
        f"CONVERSATION SO FAR:\n{transcript}\n\n"
        f"Now respond as Alex (the confused peer) to the student's latest message. "
        f"Return ONLY valid JSON."
    )

    raw = _call_with_retry(model, full_prompt, retries=retries)
    result = _parse_json_safe(raw, _FALLBACK)

    # Ensure required keys exist with correct types
    if "peer_reply" not in result or not isinstance(result.get("peer_reply"), str):
        result["peer_reply"] = _FALLBACK["peer_reply"]
    if "internal_gap_flag" not in result or not isinstance(result.get("internal_gap_flag"), bool):
        result["internal_gap_flag"] = True

    return result


# ---------------------------------------------------------------------------
# Diagnostic report (end-of-session)
# ---------------------------------------------------------------------------

def get_diagnostic_report(
    topic: str,
    conversation_history: list[dict],
) -> dict:
    """Generate a diagnostic report scoring the student's explanation.

    Args:
        topic: The concept that was explained.
        conversation_history: Full session conversation.

    Returns:
        A dict with:
            - "clarity_score" (int 1-10)
            - "correct_points" (list of strings)
            - "misconception_found" (str or None)
            - "correct_explanation" (str or None)
            - "weak_subtopic" (str or None)
    """
    _FALLBACK = {
        "clarity_score": 5,
        "correct_points": ["Could not generate a full report — please try again."],
        "misconception_found": None,
        "correct_explanation": None,
        "weak_subtopic": None,
    }

    model = _get_model(use_json_mode=True)
    if model is None:
        return _FALLBACK

    transcript = format_history(conversation_history)

    prompt = f"""
You are an expert educational assessor. A student just explained the topic "{topic}"
to a peer student in the following conversation. Assess the student's understanding.

CONVERSATION TRANSCRIPT:
{transcript}

Produce a diagnostic report as valid JSON with EXACTLY these keys:
{{
  "clarity_score": <integer 1-10, where 10 is perfect understanding>,
  "correct_points": [<short string>, ...],
  "misconception_found": <string describing the main misconception, or null>,
  "correct_explanation": <string with the correct explanation if a misconception was found, or null>,
  "weak_subtopic": <very short string naming the sub-concept the student was weakest on, or null>
}}

Scoring guide:
- 8-10: Solid, mostly accurate explanation with only minor gaps
- 5-7: Partial understanding, some key ideas right but gaps present
- 1-4: Fundamental misconceptions or very vague understanding

Return ONLY the JSON object. No markdown, no extra text.
""".strip()

    raw = _call_with_retry(model, prompt, retries=2)
    result = _parse_json_safe(raw, _FALLBACK)

    # Validate and coerce types
    try:
        result["clarity_score"] = int(result.get("clarity_score", 5))
        result["clarity_score"] = max(1, min(10, result["clarity_score"]))
    except (TypeError, ValueError):
        result["clarity_score"] = 5

    if not isinstance(result.get("correct_points"), list):
        result["correct_points"] = []

    for key in ("misconception_found", "correct_explanation", "weak_subtopic"):
        if key not in result:
            result[key] = None

    return result


# ---------------------------------------------------------------------------
# Error Hunt Mode functions
# ---------------------------------------------------------------------------

def generate_flawed_explanation(topic: str) -> str:
    """Generate a 3-5 sentence explanation of the topic with one planted factual error.

    The error is not revealed in the text — the student must find it.

    Returns:
        The flawed explanation as a plain string, or an error message string
        if the API call fails.
    """
    model = _get_model(use_json_mode=False)
    if model is None:
        return (
            "⚠️ AI is unavailable. Please add your GEMINI_API_KEY to .env and restart."
        )

    prompt = f"""
Write a 3-5 sentence explanation of "{topic}" suitable for a high school student.
Plant EXACTLY ONE subtle factual error in the explanation.
The error should sound plausible but be scientifically/mathematically wrong.
Do NOT mark, highlight, or mention the error — it should blend in naturally.
Write only the explanation paragraph, nothing else.
""".strip()

    raw = _call_with_retry(model, prompt, retries=2)
    if raw is None:
        return "⚠️ Could not generate an explanation. Please try again."

    return raw.strip()


def reveal_error_hunt_result(flawed_explanation: str, student_guess: str) -> dict:
    """Evaluate whether the student correctly identified the planted error.

    Args:
        flawed_explanation: The flawed text that was shown to the student.
        student_guess: The student's description of what they think is wrong.

    Returns:
        A dict with:
            - "correct" (bool): Whether the student found the real error.
            - "actual_error" (str): What the actual planted error was.
            - "explanation" (str): The correct version of the fact.
    """
    _FALLBACK = {
        "correct": False,
        "actual_error": "Could not determine the error automatically.",
        "explanation": "Please review the explanation manually.",
    }

    model = _get_model(use_json_mode=True)
    if model is None:
        return _FALLBACK

    prompt = f"""
The following explanation has ONE planted factual error:

EXPLANATION:
{flawed_explanation}

A student guessed this is the error:
STUDENT GUESS: {student_guess}

Evaluate whether the student identified the correct error (even if their wording
differs from the exact planted error — accept paraphrases of the same idea).

Return ONLY valid JSON with exactly these keys:
{{
  "correct": <true if the student identified the real error, false otherwise>,
  "actual_error": <string: what the actual planted error was>,
  "explanation": <string: the correct factual statement that replaces the error>
}}
""".strip()

    raw = _call_with_retry(model, prompt, retries=2)
    result = _parse_json_safe(raw, _FALLBACK)

    if not isinstance(result.get("correct"), bool):
        result["correct"] = False
    for key in ("actual_error", "explanation"):
        if not isinstance(result.get(key), str):
            result[key] = _FALLBACK[key]

    return result
