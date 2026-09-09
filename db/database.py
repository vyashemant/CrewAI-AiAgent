import os
import json
import logging
import sqlite3
from typing import Optional, List, Dict, Any
from abc import ABC, abstractmethod
from contextlib import contextmanager

logger = logging.getLogger(__name__)

DB_DIR = "data"
DB_PATH = os.path.join(DB_DIR, "research.db")

class PersistenceError(Exception):
    """Raised when a database operation fails."""
    pass

class DatabaseBackend(ABC):
    @abstractmethod
    def init_db(self, db_path=None):
        pass

    @abstractmethod
    def create_job(self, job_id: str, company: str, ticker: str, status: str, created_at: str, db_path=None):
        pass

    @abstractmethod
    def update_job(self, job_id: str, status: str, result_json: str = None, error: str = None, 
                   completed_at: str = None, db_path=None, 
                   canonical_evidence_json: str = None, consistency_json: str = None, 
                   evaluation_json: str = None, timings_json: str = None):
        pass

    @abstractmethod
    def get_job(self, job_id: str, db_path=None) -> Optional[dict]:
        pass

    @abstractmethod
    def list_jobs(self, limit: int = 20, db_path=None) -> list:
        pass


class SQLiteBackend(DatabaseBackend):
    @contextmanager
    def _get_db_connection(self, db_path=None):
        db_path = db_path or DB_PATH
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        except sqlite3.Error as e:
            logger.error(f"SQLite error: {e}")
            raise PersistenceError(f"SQLite operation failed") from e
        finally:
            conn.close()

    def init_db(self, db_path=None):
        db_path = db_path or DB_PATH
        db_dir = os.path.dirname(db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)
            
        with self._get_db_connection(db_path) as conn:
            cursor = conn.cursor()
            # Adding newer JSON columns to SQLite table mapping
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS research_jobs (
                    job_id TEXT PRIMARY KEY,
                    company TEXT NOT NULL,
                    ticker TEXT NOT NULL,
                    status TEXT NOT NULL,
                    result_json TEXT,
                    canonical_evidence_json TEXT,
                    consistency_json TEXT,
                    evaluation_json TEXT,
                    timings_json TEXT,
                    error TEXT,
                    created_at TEXT NOT NULL,
                    completed_at TEXT
                )
            """)
            
            # Check for existing schema that might be missing newer columns
            cursor.execute("PRAGMA table_info(research_jobs)")
            columns = [info[1] for info in cursor.fetchall()]
            
            required_columns = [
                "canonical_evidence_json",
                "consistency_json",
                "evaluation_json",
                "timings_json"
            ]
            
            for col in required_columns:
                if col not in columns:
                    cursor.execute(f"ALTER TABLE research_jobs ADD COLUMN {col} TEXT")
            
            conn.commit()

    def create_job(self, job_id: str, company: str, ticker: str, status: str, created_at: str, db_path=None):
        try:
            with self._get_db_connection(db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO research_jobs (job_id, company, ticker, status, created_at)
                    VALUES (?, ?, ?, ?, ?)
                """, (job_id, company, ticker, status, created_at))
                conn.commit()
        except Exception as e:
            raise PersistenceError("SQLite create_job failed") from e

    def update_job(self, job_id: str, status: str, result_json: str = None, error: str = None, 
                   completed_at: str = None, db_path=None, 
                   canonical_evidence_json: str = None, consistency_json: str = None, 
                   evaluation_json: str = None, timings_json: str = None):
        try:
            with self._get_db_connection(db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE research_jobs
                    SET status = ?, 
                        result_json = COALESCE(?, result_json), 
                        canonical_evidence_json = COALESCE(?, canonical_evidence_json),
                        consistency_json = COALESCE(?, consistency_json),
                        evaluation_json = COALESCE(?, evaluation_json),
                        timings_json = COALESCE(?, timings_json),
                        error = COALESCE(?, error), 
                        completed_at = COALESCE(?, completed_at)
                    WHERE job_id = ?
                """, (status, result_json, canonical_evidence_json, consistency_json, evaluation_json, timings_json, error, completed_at, job_id))
                conn.commit()
        except Exception as e:
            raise PersistenceError("SQLite update_job failed") from e

    def get_job(self, job_id: str, db_path=None) -> Optional[dict]:
        try:
            with self._get_db_connection(db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM research_jobs WHERE job_id = ?", (job_id,))
                row = cursor.fetchone()
                if row:
                    return dict(row)
                return None
        except Exception as e:
            raise PersistenceError("SQLite get_job failed") from e

    def list_jobs(self, limit: int = 20, db_path=None) -> list:
        try:
            with self._get_db_connection(db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT job_id, company, ticker, status, created_at, completed_at 
                    FROM research_jobs 
                    ORDER BY created_at DESC 
                    LIMIT ?
                """, (limit,))
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            raise PersistenceError("SQLite list_jobs failed") from e


class SupabaseBackend(DatabaseBackend):
    def __init__(self):
        self._client = None
        self._initialize_client()

    def _initialize_client(self):
        url = os.environ.get("SUPABASE_URL")
        key = os.environ.get("SUPABASE_SECRET_KEY")
        if not url or not key or "your_supabase_project_url" in url or "your_supabase_secret_key" in key:
            raise RuntimeError("Missing or invalid SUPABASE_URL or SUPABASE_SECRET_KEY for Supabase backend. Please configure credentials.")
        
        try:
            from supabase import create_client
            self._client = create_client(url, key)
        except Exception as e:
            logger.error(f"Failed to initialize Supabase client: {e}")
            raise RuntimeError("Failed to initialize Supabase client") from e

    def init_db(self, db_path=None):
        pass # Migrations are handled via supabase CLI

    def create_job(self, job_id: str, company: str, ticker: str, status: str, created_at: str, db_path=None):
        data = {
            "job_id": job_id,
            "company": company,
            "ticker": ticker,
            "status": status,
            "created_at": created_at
        }
        try:
            self._client.table("research_jobs").insert(data).execute()
        except Exception as e:
            logger.error(f"Supabase write error (create_job)")
            raise PersistenceError("Supabase create_job failed") from e

    def _safe_json_load(self, json_string, field_name):
        if json_string is None:
            return None
        try:
            return json.loads(json_string)
        except json.JSONDecodeError as e:
            logger.error(f"Malformed JSON in field {field_name}")
            raise PersistenceError(f"Malformed JSON in field {field_name}") from e

    def update_job(self, job_id: str, status: str, result_json: str = None, error: str = None, 
                   completed_at: str = None, db_path=None, 
                   canonical_evidence_json: str = None, consistency_json: str = None, 
                   evaluation_json: str = None, timings_json: str = None):
        
        updates = {"status": status}
        if error is not None: updates["error"] = error
        if completed_at is not None: updates["completed_at"] = completed_at
        
        # Parse JSON fields to objects before sending to JSONB
        if result_json is not None: 
            updates["result_json"] = self._safe_json_load(result_json, "result_json")
        if canonical_evidence_json is not None: 
            updates["canonical_evidence_json"] = self._safe_json_load(canonical_evidence_json, "canonical_evidence_json")
        if consistency_json is not None: 
            updates["consistency_json"] = self._safe_json_load(consistency_json, "consistency_json")
        if evaluation_json is not None: 
            updates["evaluation_json"] = self._safe_json_load(evaluation_json, "evaluation_json")
        if timings_json is not None: 
            updates["timings_json"] = self._safe_json_load(timings_json, "timings_json")

        try:
            self._client.table("research_jobs").update(updates).eq("job_id", job_id).execute()
        except Exception as e:
            logger.error(f"Supabase write error (update_job)")
            raise PersistenceError("Supabase update_job failed") from e

    def get_job(self, job_id: str, db_path=None) -> Optional[dict]:
        try:
            response = self._client.table("research_jobs").select("*").eq("job_id", job_id).execute()
            if response.data:
                row = response.data[0]
                # Convert dict/lists back to strings for API compatibility
                for key in ["result_json", "canonical_evidence_json", "consistency_json", "evaluation_json", "timings_json"]:
                    if key in row and isinstance(row[key], (dict, list)):
                        row[key] = json.dumps(row[key])
                return row
            return None
        except Exception as e:
            logger.error(f"Supabase read error (get_job)")
            raise PersistenceError("Supabase get_job failed") from e

    def list_jobs(self, limit: int = 20, db_path=None) -> list:
        try:
            response = self._client.table("research_jobs").select("job_id, company, ticker, status, created_at, completed_at").order("created_at", desc=True).limit(limit).execute()
            return response.data
        except Exception as e:
            logger.error(f"Supabase read error (list_jobs)")
            raise PersistenceError("Supabase list_jobs failed") from e


class MockBackend(DatabaseBackend):
    """In-memory dictionary exclusively for explicit testing mode."""
    def __init__(self):
        self._mock_db: Dict[str, dict] = {}

    def clear(self):
        self._mock_db.clear()

    def init_db(self, db_path=None):
        pass

    def create_job(self, job_id: str, company: str, ticker: str, status: str, created_at: str, db_path=None):
        self._mock_db[job_id] = {
            "job_id": job_id,
            "company": company,
            "ticker": ticker,
            "status": status,
            "created_at": created_at
        }

    def update_job(self, job_id: str, status: str, result_json: str = None, error: str = None, 
                   completed_at: str = None, db_path=None, 
                   canonical_evidence_json: str = None, consistency_json: str = None, 
                   evaluation_json: str = None, timings_json: str = None):
        if job_id in self._mock_db:
            updates = {"status": status}
            if result_json is not None: updates["result_json"] = result_json
            if canonical_evidence_json is not None: updates["canonical_evidence_json"] = canonical_evidence_json
            if consistency_json is not None: updates["consistency_json"] = consistency_json
            if evaluation_json is not None: updates["evaluation_json"] = evaluation_json
            if timings_json is not None: updates["timings_json"] = timings_json
            if error is not None: updates["error"] = error
            if completed_at is not None: updates["completed_at"] = completed_at
            self._mock_db[job_id].update(updates)
        else:
            raise PersistenceError(f"Job {job_id} not found in mock db")

    def get_job(self, job_id: str, db_path=None) -> Optional[dict]:
        row = self._mock_db.get(job_id)
        if row:
            r = row.copy()
            # In memory, we keep them as they were stored (strings, if passed as strings)
            return r
        return None

    def list_jobs(self, limit: int = 20, db_path=None) -> list:
        jobs = list(self._mock_db.values())
        jobs.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        result = []
        for j in jobs[:limit]:
            result.append({
                "job_id": j.get("job_id"),
                "company": j.get("company"),
                "ticker": j.get("ticker"),
                "status": j.get("status"),
                "created_at": j.get("created_at"),
                "completed_at": j.get("completed_at")
            })
        return result


# Singleton setup logic
_db_instance: Optional[DatabaseBackend] = None

def get_db() -> DatabaseBackend:
    global _db_instance
    if _db_instance is not None:
        return _db_instance

    backend_type = os.environ.get("DATABASE_BACKEND", "sqlite").lower()
    
    if backend_type == "mock":
        _db_instance = MockBackend()
    elif backend_type == "supabase":
        _db_instance = SupabaseBackend()
    else:
        _db_instance = SQLiteBackend()

    return _db_instance

def init_db(db_path=None):
    get_db().init_db(db_path)

def create_job(job_id: str, company: str, ticker: str, status: str, created_at: str, db_path=None):
    get_db().create_job(job_id, company, ticker, status, created_at, db_path)

def update_job(job_id: str, status: str, result_json: str = None, error: str = None, 
               completed_at: str = None, db_path=None, 
               canonical_evidence_json: str = None, consistency_json: str = None, 
               evaluation_json: str = None, timings_json: str = None):
    get_db().update_job(job_id, status, result_json, error, completed_at, db_path, 
                        canonical_evidence_json, consistency_json, evaluation_json, timings_json)

def get_job(job_id: str, db_path=None) -> Optional[dict]:
    return get_db().get_job(job_id, db_path)

def list_jobs(limit: int = 20, db_path=None) -> list:
    return get_db().list_jobs(limit, db_path)

def set_testing_mode(enabled: bool):
    """
    Explicitly force the mock database for tests. 
    This prevents real DB side-effects during unittesting.
    """
    global _db_instance
    if enabled:
        os.environ["DATABASE_BACKEND"] = "mock"
        _db_instance = MockBackend()
    else:
        os.environ.pop("DATABASE_BACKEND", None)
        _db_instance = None

def clear_mock_db():
    if isinstance(_db_instance, MockBackend):
        _db_instance.clear()
