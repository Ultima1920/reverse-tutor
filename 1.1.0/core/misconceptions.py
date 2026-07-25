"""
core/misconceptions.py — Thin wrapper around the DB for misconception operations.

Keeps the page code clean by hiding DB import details behind domain-language
function names.
"""

from core import db


def get_misconceptions_for_topic(topic: str) -> list[tuple[str, str]]:
    """Return (misconception, correction) tuples for the given topic.

    Delegates to core.db.get_misconceptions so that page code only needs to
    import this module.
    """
    return db.get_misconceptions(topic)


def log_concept_weakness(
    student_id: int,
    topic: str,
    sub_concept: str,
    clarity_score: int,
) -> None:
    """Record or update a concept weakness for a student after a session.

    Delegates to core.db.upsert_concept_weakness.

    Args:
        student_id: The student's DB id.
        topic: The top-level topic (e.g. "Photosynthesis").
        sub_concept: The specific sub-concept that was weak (e.g. "photolysis").
        clarity_score: The AI clarity score from the diagnostic report (1-10).
    """
    db.upsert_concept_weakness(student_id, topic, sub_concept, clarity_score)
