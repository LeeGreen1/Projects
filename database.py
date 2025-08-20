import sqlite3
from pathlib import Path

DB_FILE = "assignments.db"

def get_db_connection():
    """Establishes a connection to the SQLite database."""
    con = sqlite3.connect(DB_FILE)
    con.row_factory = sqlite3.Row
    return con

def init_db():
    """Initializes the database and creates the 'assignments' table if it doesn't exist."""
    if Path(DB_FILE).exists():
        return

    print("First run: Initializing database...")
    con = get_db_connection()
    con.execute("""
        CREATE TABLE assignments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            brief_text TEXT NOT NULL,
            breakdown_text TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    con.commit()
    con.close()
    print("Database initialized successfully.")

def add_assignment(brief_text: str, breakdown_text: str):
    """Adds a new assignment brief and its breakdown to the database."""
    con = get_db_connection()
    con.execute(
        "INSERT INTO assignments (brief_text, breakdown_text) VALUES (?, ?)",
        (brief_text, breakdown_text)
    )
    con.commit()
    con.close()

def get_past_assignments(limit: int = 3) -> list[dict]:
    """Retrieves a list of the most recent assignment examples from the database."""
    con = get_db_connection()
    cursor = con.execute(
        "SELECT brief_text, breakdown_text FROM assignments ORDER BY created_at DESC LIMIT ?",
        (limit,)
    )
    assignments = [dict(row) for row in cursor.fetchall()]
    con.close()
    return assignments