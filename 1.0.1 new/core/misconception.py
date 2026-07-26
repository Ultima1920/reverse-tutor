from core.db import get_connection, upsert_concept_weakness


def get_misconceptions_for_topic(topic):
    """
    Fetches common misconceptions for a given topic from the SQLite database.
    Acts as a non-AI library lookup to steer the confused-peer persona.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT misconception, correction FROM misconception_library WHERE topic LIKE ?",
        (f"%{topic}%",)
    )
    results = cursor.fetchall()
    conn.close()
    return results


def log_concept_weakness(student_id: int, topic: str, sub_concept: str, clarity_score: int):
    """
    Records or updates a student's concept weakness in the database.
    Delegates to upsert_concept_weakness in core/db.py.
    """
    if not sub_concept:
        return  # Nothing to log if no weak subtopic was identified
    try:
        upsert_concept_weakness(student_id, topic, sub_concept, clarity_score)
    except Exception as e:
        print(f"Warning: Could not log concept weakness: {e}")
