import sqlite3
import os

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

if __name__ == "__main__":
    init_db()
    print("Database initialized.")
