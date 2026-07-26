import sqlite3
import os
import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "student.db")

def get_connection():
    return sqlite3.connect(DB_PATH)

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    # Create students table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Ensure default student exists
    cursor.execute("SELECT COUNT(*) FROM students WHERE id = 1")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO students (id, name) VALUES (1, 'Default Student')")

    # Create sessions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER,
            topic TEXT,
            started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(student_id) REFERENCES students(id)
        )
    ''')

    # Create misconception_library table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS misconception_library (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            topic TEXT NOT NULL,
            misconception TEXT NOT NULL,
            correction TEXT NOT NULL
        )
    ''')

    # Create concept_weaknesses table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS concept_weaknesses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER,
            misconception_id INTEGER,
            confidence_score REAL DEFAULT 0.0,
            FOREIGN KEY(student_id) REFERENCES students(id),
            FOREIGN KEY(misconception_id) REFERENCES misconception_library(id)
        )
    ''')
    
    # Alter sessions table to add new columns if they don't exist
    try: cursor.execute("ALTER TABLE sessions ADD COLUMN mode TEXT")
    except sqlite3.OperationalError: pass # Column exists
    
    try: cursor.execute("ALTER TABLE sessions ADD COLUMN self_rated_confidence INTEGER")
    except sqlite3.OperationalError: pass
    
    try: cursor.execute("ALTER TABLE sessions ADD COLUMN clarity_score INTEGER")
    except sqlite3.OperationalError: pass
    
    try: cursor.execute("ALTER TABLE sessions ADD COLUMN transcript TEXT")
    except sqlite3.OperationalError: pass
    
    try: cursor.execute("ALTER TABLE sessions ADD COLUMN ended_at TIMESTAMP")
    except sqlite3.OperationalError: pass

    # Alter concept_weaknesses to add new columns
    try: cursor.execute("ALTER TABLE concept_weaknesses ADD COLUMN topic TEXT")
    except sqlite3.OperationalError: pass

    try: cursor.execute("ALTER TABLE concept_weaknesses ADD COLUMN sub_concept TEXT")
    except sqlite3.OperationalError: pass
    
    try: cursor.execute("ALTER TABLE concept_weaknesses ADD COLUMN resolved BOOLEAN DEFAULT 0")
    except sqlite3.OperationalError: pass
    
    try: cursor.execute("ALTER TABLE concept_weaknesses ADD COLUMN last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
    except sqlite3.OperationalError: pass

    # Populate initial misconceptions if empty
    cursor.execute("SELECT COUNT(*) FROM misconception_library")
    if cursor.fetchone()[0] == 0:
        initial_misconceptions = [
            ("Photosynthesis", "Plants get their food from soil", "Plants make their own food using sunlight, water, and carbon dioxide."),
            ("Fractions", "1/4 is larger than 1/3 because 4 is larger than 3", "In fractions, a larger denominator means the whole is divided into more, smaller pieces."),
            ("Gravity", "Heavy objects fall faster than light objects", "In a vacuum, all objects fall at the same rate regardless of mass. Air resistance affects falling speed on Earth.")
        ]
        cursor.executemany("INSERT INTO misconception_library (topic, misconception, correction) VALUES (?, ?, ?)", initial_misconceptions)

    conn.commit()
    conn.close()

# --- New Helper Functions ---

def create_session(student_id, topic, mode, self_rated_confidence):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO sessions (student_id, topic, mode, self_rated_confidence)
        VALUES (?, ?, ?, ?)
    ''', (student_id, topic, mode, self_rated_confidence))
    session_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return session_id

def update_session_result(session_id, clarity_score, transcript):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE sessions
        SET clarity_score = ?, transcript = ?, ended_at = CURRENT_TIMESTAMP
        WHERE id = ?
    ''', (clarity_score, transcript, session_id))
    conn.commit()
    conn.close()

def get_unresolved_weaknesses(student_id):
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, topic, sub_concept, confidence_score, last_seen
        FROM concept_weaknesses
        WHERE student_id = ? AND resolved = 0
        ORDER BY last_seen DESC
    ''', (student_id,))
    results = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return results

def upsert_concept_weakness(student_id, topic, sub_concept, clarity_score):
    """
    Upserts a weakness. If the student has struggled with this sub_concept before, update it.
    If clarity_score is high (e.g. >= 7), we might mark it resolved.
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    # Check if exists
    cursor.execute('''
        SELECT id FROM concept_weaknesses
        WHERE student_id = ? AND topic = ? AND sub_concept = ?
    ''', (student_id, topic, sub_concept))
    row = cursor.fetchone()
    
    is_resolved = 1 if clarity_score >= 7 else 0

    if row:
        # Update existing
        cursor.execute('''
            UPDATE concept_weaknesses
            SET confidence_score = ?, resolved = ?, last_seen = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (clarity_score, is_resolved, row[0]))
    else:
        # Insert new
        cursor.execute('''
            INSERT INTO concept_weaknesses (student_id, topic, sub_concept, confidence_score, resolved)
            VALUES (?, ?, ?, ?, ?)
        ''', (student_id, topic, sub_concept, clarity_score, is_resolved))
        
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    print("Database initialized/updated.")
