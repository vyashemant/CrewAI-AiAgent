import sqlite3
import os
import json
from contextlib import contextmanager

DB_DIR = "data"
DB_PATH = os.path.join(DB_DIR, "research.db")

def init_db(db_path=None):
    """Initialize the database and create tables if they do not exist."""
    db_path = db_path or DB_PATH
    # Ensure data directory exists
    db_dir = os.path.dirname(db_path)
    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir, exist_ok=True)
        
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS research_jobs (
                job_id TEXT PRIMARY KEY,
                company TEXT NOT NULL,
                ticker TEXT NOT NULL,
                status TEXT NOT NULL,
                result_json TEXT,
                error TEXT,
                created_at TEXT NOT NULL,
                completed_at TEXT
            )
        """)
        conn.commit()

@contextmanager
def get_db_connection(db_path=None):
    """Context manager for SQLite database connection."""
    db_path = db_path or DB_PATH
    conn = sqlite3.connect(db_path)
    # Return rows as dictionaries
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

def create_job(job_id: str, company: str, ticker: str, status: str, created_at: str, db_path=None):
    """Create a new research job record."""
    db_path = db_path or DB_PATH
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO research_jobs (job_id, company, ticker, status, created_at)
            VALUES (?, ?, ?, ?, ?)
        """, (job_id, company, ticker, status, created_at))
        conn.commit()

def update_job(job_id: str, status: str, result_json: str = None, error: str = None, completed_at: str = None, db_path=None):
    """Update an existing research job."""
    db_path = db_path or DB_PATH
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE research_jobs
            SET status = ?, result_json = COALESCE(?, result_json), error = COALESCE(?, error), completed_at = COALESCE(?, completed_at)
            WHERE job_id = ?
        """, (status, result_json, error, completed_at, job_id))
        conn.commit()

def get_job(job_id: str, db_path=None) -> dict:
    """Retrieve a job by its ID."""
    db_path = db_path or DB_PATH
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM research_jobs WHERE job_id = ?", (job_id,))
        row = cursor.fetchone()
        if row:
            return dict(row)
        return None

def list_jobs(limit: int = 20, db_path=None) -> list:
    """List most recent jobs up to the specified limit."""
    db_path = db_path or DB_PATH
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT job_id, company, ticker, status, created_at, completed_at 
            FROM research_jobs 
            ORDER BY created_at DESC 
            LIMIT ?
        """, (limit,))
        return [dict(row) for row in cursor.fetchall()]
