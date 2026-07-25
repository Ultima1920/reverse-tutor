"""
core/db.py — SQLite database layer for Reverse Tutor AI.

Handles:
- Schema creation and initial seed data
- All read/write helper functions used by the app pages and core modules
- DB_PATH points to data/reverse_tutor.db (created automatically)
"""

import sqlite3
import os
from pathlib import Path
from datetime import datetime

# ---------------------------------------------------------------------------
# Path configuration
# ---------------------------------------------------------------------------

# Resolve project root relative to this file, then point to data/
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = _PROJECT_ROOT / "data"
DB_PATH = DATA_DIR / "reverse_tutor.db"


# ---------------------------------------------------------------------------
# Connection helper
# ---------------------------------------------------------------------------

def get_connection() -> sqlite3.Connection:
    """Return a sqlite3 connection to the project database.
    Creates the data/ directory if it doesn't exist yet.
    """
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    # Return rows as dict-like sqlite3.Row objects so callers can use column names
    conn.row_factory = sqlite3.Row
    return conn


# ---------------------------------------------------------------------------
# Schema & seed data
# ---------------------------------------------------------------------------

# Seed misconceptions inserted on first init
_SEED_MISCONCEPTIONS = [
    (
        "Photosynthesis",
        "Plants get their food from soil",
        "Plants make their own food using sunlight, water, and carbon dioxide; "
        "soil mainly provides water and minerals, not food itself.",
    ),
    (
        "Photosynthesis",
        "The oxygen plants release comes from carbon dioxide",
        "The released oxygen actually comes from water molecules being split apart "
        "(photolysis); the carbon from CO2 is used to build sugar.",
    ),
    (
        "Fractions",
        "1/4 is larger than 1/3 because 4 is larger than 3",
        "A larger denominator means the whole is divided into more, smaller pieces, "
        "so 1/4 is actually smaller than 1/3.",
    ),
    (
        "Gravity",
        "Heavy objects fall faster than light objects",
        "In a vacuum, all objects fall at the same rate regardless of mass; "
        "air resistance is what makes light objects appear to fall slower on Earth.",
    ),
    (
        "Newton's Third Law",
        "Equal and opposite forces cancel out so nothing should move",
        "The two forces act on DIFFERENT objects, so they don't cancel; that's why "
        "a rocket can still accelerate even though it pushes gas one way and gas "
        "pushes it the other.",
    ),
    (
        "Supply and Demand",
        "Higher demand always means higher price, regardless of supply",
        "Price depends on the relationship between supply AND demand together; "
        "if supply rises just as much as demand, price can stay flat.",
    ),
]


def init_db() -> None:
    """Create all tables if they don't exist, then seed misconception data.

    Safe to call multiple times — uses CREATE TABLE IF NOT EXISTS and only
    inserts seed rows when the table is empty, so re-running is idempotent.
    """
    conn = get_connection()
    try:
        cur = conn.cursor()

        # -- students table -------------------------------------------------
        cur.execute("""
            CREATE TABLE IF NOT EXISTS students (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                name       TEXT    NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # -- sessions table -------------------------------------------------
        cur.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                id                   INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id           INTEGER NOT NULL,
                topic                TEXT    NOT NULL,
                mode                 TEXT    NOT NULL,
                self_rated_confidence INTEGER,
                clarity_score        INTEGER,
                transcript           TEXT,
                started_at           TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                ended_at             TIMESTAMP,
                FOREIGN KEY (student_id) REFERENCES students (id)
            )
        """)

        # -- misconception_library table ------------------------------------
        cur.execute("""
            CREATE TABLE IF NOT EXISTS misconception_library (
                id           INTEGER PRIMARY KEY AUTOINCREMENT,
                topic        TEXT NOT NULL,
                misconception TEXT NOT NULL,
                correction   TEXT NOT NULL
            )
        """)

        # -- concept_weaknesses table ---------------------------------------
        cur.execute("""
            CREATE TABLE IF NOT EXISTS concept_weaknesses (
                id               INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id       INTEGER NOT NULL,
                topic            TEXT    NOT NULL,
                sub_concept      TEXT    NOT NULL,
                last_clarity_score INTEGER,
                resolved         BOOLEAN DEFAULT 0,
                last_seen        TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (student_id) REFERENCES students (id)
            )
        """)

        conn.commit()

        # Seed misconceptions only if the table is currently empty
        count = cur.execute("SELECT COUNT(*) FROM misconception_library").fetchone()[0]
        if count == 0:
            cur.executemany(
                "INSERT INTO misconception_library (topic, misconception, correction) VALUES (?, ?, ?)",
                _SEED_MISCONCEPTIONS,
            )
            conn.commit()
            print(f"[db] Seeded {len(_SEED_MISCONCEPTIONS)} misconceptions.")

        print("[db] Database initialised successfully.")
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# Student helpers
# ---------------------------------------------------------------------------

def get_or_create_default_student(name: str = "Student") -> int:
    """Return the id of the first student row with the given name,
    creating one if it doesn't exist.  Used for the single-user hackathon demo.
    """
    conn = get_connection()
    try:
        cur = conn.cursor()
        row = cur.execute(
            "SELECT id FROM students WHERE name = ? LIMIT 1", (name,)
        ).fetchone()
        if row:
            return row["id"]
        cur.execute("INSERT INTO students (name) VALUES (?)", (name,))
        conn.commit()
        return cur.lastrowid
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# Session helpers
# ---------------------------------------------------------------------------

def create_session(
    student_id: int,
    topic: str,
    mode: str,
    self_rated_confidence: int,
) -> int:
    """Insert a new session row and return its id."""
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO sessions (student_id, topic, mode, self_rated_confidence)
            VALUES (?, ?, ?, ?)
            """,
            (student_id, topic, mode, self_rated_confidence),
        )
        conn.commit()
        return cur.lastrowid
    finally:
        conn.close()


def update_session_result(
    session_id: int,
    clarity_score: int,
    transcript: str,
) -> None:
    """Write the AI-generated clarity_score and full transcript to an existing session."""
    conn = get_connection()
    try:
        conn.execute(
            """
            UPDATE sessions
            SET clarity_score = ?,
                transcript    = ?,
                ended_at      = ?
            WHERE id = ?
            """,
            (clarity_score, transcript, datetime.utcnow().isoformat(), session_id),
        )
        conn.commit()
    finally:
        conn.close()


def get_sessions_for_student(student_id: int) -> list:
    """Return all session rows for a student, newest first."""
    conn = get_connection()
    try:
        rows = conn.execute(
            """
            SELECT id, topic, mode, self_rated_confidence, clarity_score, started_at, ended_at
            FROM sessions
            WHERE student_id = ?
            ORDER BY started_at DESC
            """,
            (student_id,),
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# Concept weakness helpers
# ---------------------------------------------------------------------------

def upsert_concept_weakness(
    student_id: int,
    topic: str,
    sub_concept: str,
    clarity_score: int,
) -> None:
    """Insert or update a concept weakness entry for a student.
    If an unresolved row already exists for the same (student, topic, sub_concept),
    update its score and timestamp; otherwise insert a fresh row.
    """
    conn = get_connection()
    try:
        existing = conn.execute(
            """
            SELECT id FROM concept_weaknesses
            WHERE student_id = ? AND topic = ? AND sub_concept = ? AND resolved = 0
            LIMIT 1
            """,
            (student_id, topic, sub_concept),
        ).fetchone()

        if existing:
            conn.execute(
                """
                UPDATE concept_weaknesses
                SET last_clarity_score = ?,
                    last_seen = ?
                WHERE id = ?
                """,
                (clarity_score, datetime.utcnow().isoformat(), existing["id"]),
            )
        else:
            conn.execute(
                """
                INSERT INTO concept_weaknesses
                    (student_id, topic, sub_concept, last_clarity_score, last_seen)
                VALUES (?, ?, ?, ?, ?)
                """,
                (student_id, topic, sub_concept, clarity_score, datetime.utcnow().isoformat()),
            )
        conn.commit()
    finally:
        conn.close()


def get_unresolved_weaknesses(student_id: int) -> list:
    """Return all unresolved concept weaknesses for a student."""
    conn = get_connection()
    try:
        rows = conn.execute(
            """
            SELECT id, topic, sub_concept, last_clarity_score, last_seen
            FROM concept_weaknesses
            WHERE student_id = ? AND resolved = 0
            ORDER BY last_seen DESC
            """,
            (student_id,),
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# Misconception library helpers
# ---------------------------------------------------------------------------

def get_misconceptions(topic: str) -> list[tuple[str, str]]:
    """Return (misconception, correction) tuples for the given topic."""
    conn = get_connection()
    try:
        rows = conn.execute(
            "SELECT misconception, correction FROM misconception_library WHERE topic = ?",
            (topic,),
        ).fetchall()
        return [(r["misconception"], r["correction"]) for r in rows]
    finally:
        conn.close()


def get_all_misconceptions() -> list:
    """Return all rows from misconception_library as dicts."""
    conn = get_connection()
    try:
        rows = conn.execute(
            "SELECT id, topic, misconception, correction FROM misconception_library ORDER BY topic"
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def get_all_topics() -> list[str]:
    """Return distinct topics present in misconception_library."""
    conn = get_connection()
    try:
        rows = conn.execute(
            "SELECT DISTINCT topic FROM misconception_library ORDER BY topic"
        ).fetchall()
        return [r["topic"] for r in rows]
    finally:
        conn.close()
