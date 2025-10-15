import sqlite3
import json

DATABASE_NAME = "resume_database.db"

def init_db():
    """Initializes the database and creates the resumes table if it doesn't exist."""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS resumes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        filename TEXT NOT NULL UNIQUE,
        original_text TEXT NOT NULL,
        parsed_json TEXT
    );
    """)
    conn.commit()
    conn.close()

def add_resume(filename, original_text, parsed_json):
    """Adds a new resume's data to the database, or updates it if it exists."""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO resumes (filename, original_text, parsed_json) 
    VALUES (?, ?, ?)
    ON CONFLICT(filename) 
    DO UPDATE SET original_text=excluded.original_text, parsed_json=excluded.parsed_json;
    """, (filename, original_text, json.dumps(parsed_json)))
    conn.commit()
    conn.close()

def get_all_resumes():
    """Retrieves all resumes from the database."""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT filename, original_text FROM resumes;")
    resumes = cursor.fetchall()
    conn.close()
    return resumes