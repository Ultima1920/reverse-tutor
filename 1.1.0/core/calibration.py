"""
core/calibration.py — Difficulty calibration and confidence gap calculator.

Two responsibilities:
1. adjust_difficulty: looks at the history of gap flags to decide whether to
   make the confused peer easier or harder to satisfy.
2. compute_calibration_gap: compares self-rated confidence vs. AI clarity score
   to tell the student how well-calibrated their self-assessment is.
"""


# ---------------------------------------------------------------------------
# Difficulty adjustment
# ---------------------------------------------------------------------------

def adjust_difficulty(gap_flag_history: list[bool]) -> str:
    """Decide the difficulty level for the next conversation turn.

    The logic is deliberately simple and commented for hackathon judges:

    - If we have fewer than 2 data points, stay at "standard" (not enough info).
    - Look at the most recent 3 flags (or all of them if fewer than 3).
    - If ALL recent flags are True (student keeps making gaps) → use "gentle"
      so the peer asks simpler, more forgiving questions.
    - If ALL recent flags are False (student is nailing it) → use "challenging"
      so the peer digs into nuance and edge cases.
    - Mixed results → stay at "standard".

    Args:
        gap_flag_history: List of booleans from the model's internal_gap_flag.
            True means a fundamental gap was still present in that turn.

    Returns:
        One of "gentle", "standard", or "challenging".
    """
    if len(gap_flag_history) < 2:
        # Not enough history yet — start at standard difficulty
        return "standard"

    # Consider only the most recent window of turns
    window = gap_flag_history[-3:]

    all_gaps = all(flag is True for flag in window)       # Student struggling
    no_gaps = all(flag is False for flag in window)       # Student excelling

    if all_gaps:
        return "gentle"       # Student needs easier questions
    elif no_gaps:
        return "challenging"  # Student can handle harder probing
    else:
        return "standard"     # Mixed — stay balanced


# ---------------------------------------------------------------------------
# Calibration gap calculator
# ---------------------------------------------------------------------------

def compute_calibration_gap(
    self_rated_confidence: int,
    clarity_score: int,
) -> dict:
    """Calculate how well the student's self-assessment matches their actual performance.

    Args:
        self_rated_confidence: Student's pre-session confidence rating (1-10).
        clarity_score: AI-generated clarity score from the diagnostic report (1-10).

    Returns:
        A dict with:
            - "gap" (int): self_rated_confidence minus clarity_score.
                Positive = overconfident, negative = underconfident.
            - "label" (str): "overconfident", "underconfident", or "well-calibrated".
            - "self_rated" (int): original self-rated value (for display).
            - "clarity" (int): original clarity score (for display).
    """
    gap = self_rated_confidence - clarity_score

    # Threshold: a gap of more than 1 in either direction is notable
    if gap > 1:
        label = "overconfident"
    elif gap < -1:
        label = "underconfident"
    else:
        label = "well-calibrated"

    return {
        "gap": gap,
        "label": label,
        "self_rated": self_rated_confidence,
        "clarity": clarity_score,
    }
