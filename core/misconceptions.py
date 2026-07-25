from core.db import get_connection

def get_misconceptions_for_topic(topic):
    """
    Fetches common misconceptions for a given topic from the SQLite database.
    This acts as the non-AI, instant library lookup to reduce Gemini calls and steer the persona.
    """
    conn = get_connection()
    cursor = conn.cursor()
    # Simple LIKE matching for demo purposes
    cursor.execute("SELECT misconception, correction FROM misconception_library WHERE topic LIKE ?", (f"%{topic}%",))
    results = cursor.fetchall()
    conn.close()
    return results

def log_concept_weakness(student_id, misconception_id, score_change):
    """
    Stub for adaptive difficulty tracking.
    """
    pass
