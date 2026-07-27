def adjust_difficulty(internal_gap_flag_history: list) -> str:
    """
    Adjusts the difficulty of the peer's questions based on the recent
    pattern of internal_gap_flag values (True = student still has gaps).

    Logic:
    - If mostly True (>60%) -> student is struggling -> return "gentle"
    - If mostly False (<40% True) -> student is doing well -> return "challenging"
    - Otherwise -> return "standard"
    """
    if not internal_gap_flag_history:
        return "standard"

    # Consider only the last 5 turns for recency
    recent = internal_gap_flag_history[-5:]
    gap_count = sum(1 for flag in recent if flag)
    gap_ratio = gap_count / len(recent)

    if gap_ratio > 0.6:
        return "gentle"
    elif gap_ratio < 0.4:
        return "challenging"
    else:
        return "standard"


def compute_calibration_gap(self_rated_confidence: int, clarity_score: int) -> dict:
    """
    Compares how the student thought they'd do vs. how they actually did.

    self_rated_confidence: 1-10 (student's pre-session self-rating)
    clarity_score: 1-10 (AI-assigned score after the session)

    Returns:
    {
        "gap": int (signed; positive = overconfident, negative = underconfident),
        "label": "overconfident" | "underconfident" | "well-calibrated"
    }
    """
    gap = self_rated_confidence - clarity_score

    if gap >= 2:
        label = "overconfident"
    elif gap <= -2:
        label = "underconfident"
    else:
        label = "well-calibrated"

    return {"gap": gap, "label": label}
