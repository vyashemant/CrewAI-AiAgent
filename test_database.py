import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime, timezone
import json
import os
import db.database as db
from db.database import PersistenceError, SQLiteBackend, SupabaseBackend, MockBackend

@pytest.fixture(autouse=True)
def cleanup_env():
    # Make sure we don't leak env vars across tests
    original_backend = os.environ.get("DATABASE_BACKEND")
    yield
    if original_backend is None:
        os.environ.pop("DATABASE_BACKEND", None)
    else:
        os.environ["DATABASE_BACKEND"] = original_backend

def test_backend_selection_sqlite():
    os.environ["DATABASE_BACKEND"] = "sqlite"
    # force reload instance
    db._db_instance = None
    backend = db.get_db()
    assert isinstance(backend, SQLiteBackend)

def test_sqlite_schema_migration(tmp_path):
    # Test that init_db safely adds missing columns to an old schema
    db_path = str(tmp_path / "test_research.db")
    
    # 1. Create old schema without the 4 new JSON columns
    import sqlite3
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE research_jobs (
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
        
    # 2. Run init_db which should alter the table
    backend = SQLiteBackend()
    backend.init_db(db_path=db_path)
    
    # 3. Verify columns exist
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(research_jobs)")
        columns = [info[1] for info in cursor.fetchall()]
        
        assert "canonical_evidence_json" in columns
        assert "consistency_json" in columns
        assert "evaluation_json" in columns
        assert "timings_json" in columns
        assert "result_json" in columns

def test_backend_selection_mock():
    os.environ["DATABASE_BACKEND"] = "mock"
    db._db_instance = None
    backend = db.get_db()
    assert isinstance(backend, MockBackend)

def test_backend_selection_supabase_missing_creds():
    os.environ["DATABASE_BACKEND"] = "supabase"
    os.environ["SUPABASE_URL"] = ""
    os.environ["SUPABASE_SECRET_KEY"] = ""
    db._db_instance = None
    with pytest.raises(RuntimeError, match="Missing or invalid SUPABASE_URL"):
        db.get_db()

@patch("db.database.SupabaseBackend._initialize_client")
def test_backend_selection_supabase_valid(mock_init):
    os.environ["DATABASE_BACKEND"] = "supabase"
    os.environ["SUPABASE_URL"] = "https://real-url.supabase.co"
    os.environ["SUPABASE_SECRET_KEY"] = "real-key"
    db._db_instance = None
    backend = db.get_db()
    assert isinstance(backend, SupabaseBackend)
    mock_init.assert_called_once()

@pytest.fixture
def mock_db():
    db.set_testing_mode(True)
    db.clear_mock_db()
    yield
    db.clear_mock_db()
    db.set_testing_mode(False)

def test_create_get_job_mock(mock_db):
    now_str = datetime.now(timezone.utc).isoformat()
    db.create_job("job-1", "Company", "TICK", "queued", now_str)
    
    job = db.get_job("job-1")
    assert job is not None
    assert job["job_id"] == "job-1"
    assert job["company"] == "Company"
    assert job["ticker"] == "TICK"
    assert job["status"] == "queued"
    assert job["created_at"] == now_str

def test_get_missing_job_mock(mock_db):
    job = db.get_job("non-existent")
    assert job is None

def test_update_job_mock(mock_db):
    now_str = datetime.now(timezone.utc).isoformat()
    db.create_job("job-1", "Company", "TICK", "queued", now_str)
    
    # Update to running
    db.update_job("job-1", status="running")
    job = db.get_job("job-1")
    assert job["status"] == "running"
    
    # Update to completed with results
    completed_time = datetime.now(timezone.utc).isoformat()
    db.update_job(
        "job-1",
        status="completed",
        result_json='{"some": "data"}',
        canonical_evidence_json='{"evidence": []}',
        consistency_json='{"status": "ok"}',
        evaluation_json='{"score": 1.0}',
        timings_json='{"total": 10}',
        completed_at=completed_time
    )
    
    job2 = db.get_job("job-1")
    assert job2["status"] == "completed"
    assert job2["result_json"] == '{"some": "data"}'
    assert job2["canonical_evidence_json"] == '{"evidence": []}'
    assert job2["consistency_json"] == '{"status": "ok"}'
    assert job2["evaluation_json"] == '{"score": 1.0}'
    assert job2["timings_json"] == '{"total": 10}'
    assert job2["completed_at"] == completed_time

def test_list_jobs_ordering_and_limit_mock(mock_db):
    db.create_job("job-1", "A", "A", "queued", "2026-08-01T10:00:00")
    db.create_job("job-2", "B", "B", "queued", "2026-08-03T10:00:00")
    db.create_job("job-3", "C", "C", "queued", "2026-08-02T10:00:00")
    
    # Ordering should be by created_at DESC
    jobs = db.list_jobs(limit=2)
    assert len(jobs) == 2
    assert jobs[0]["job_id"] == "job-2" # Newest
    assert jobs[1]["job_id"] == "job-3"

def test_failed_result_mock(mock_db):
    now_str = datetime.now(timezone.utc).isoformat()
    db.create_job("job-1", "Company", "TICK", "queued", now_str)
    
    db.update_job("job-1", status="failed", error="Something went wrong")
    job = db.get_job("job-1")
    assert job["status"] == "failed"
    assert job["error"] == "Something went wrong"


# --- MOCKED SUPABASE TESTS ---
@patch("db.database.SupabaseBackend._initialize_client")
def test_supabase_create_job(mock_init):
    os.environ["DATABASE_BACKEND"] = "supabase"
    os.environ["SUPABASE_URL"] = "https://real-url.supabase.co"
    os.environ["SUPABASE_SECRET_KEY"] = "real-key"
    db._db_instance = None
    backend = db.get_db()
    backend._client = MagicMock()
    
    mock_table = MagicMock()
    backend._client.table.return_value = mock_table
    
    backend.create_job("job-1", "Company", "TICK", "queued", "2026-01-01T00:00:00")
    
    backend._client.table.assert_called_with("research_jobs")
    mock_table.insert.assert_called_once_with({
        "job_id": "job-1",
        "company": "Company",
        "ticker": "TICK",
        "status": "queued",
        "created_at": "2026-01-01T00:00:00"
    })
    mock_table.insert().execute.assert_called_once()

@patch("db.database.SupabaseBackend._initialize_client")
def test_supabase_update_job_valid_json(mock_init):
    os.environ["DATABASE_BACKEND"] = "supabase"
    os.environ["SUPABASE_URL"] = "https://real-url.supabase.co"
    os.environ["SUPABASE_SECRET_KEY"] = "real-key"
    db._db_instance = None
    backend = db.get_db()
    backend._client = MagicMock()
    
    mock_table = MagicMock()
    backend._client.table.return_value = mock_table
    
    backend.update_job("job-1", "completed", result_json='{"key": "value"}')
    
    mock_table.update.assert_called_once_with({
        "status": "completed",
        "result_json": {"key": "value"}
    })

@patch("db.database.SupabaseBackend._initialize_client")
def test_supabase_update_job_malformed_json(mock_init):
    os.environ["DATABASE_BACKEND"] = "supabase"
    os.environ["SUPABASE_URL"] = "https://real-url.supabase.co"
    os.environ["SUPABASE_SECRET_KEY"] = "real-key"
    db._db_instance = None
    backend = db.get_db()
    backend._client = MagicMock()
    
    with pytest.raises(PersistenceError, match="Malformed JSON in field result_json"):
        backend.update_job("job-1", "completed", result_json='{bad json}')

@patch("db.database.SupabaseBackend._initialize_client")
def test_supabase_create_job_failure(mock_init):
    os.environ["DATABASE_BACKEND"] = "supabase"
    os.environ["SUPABASE_URL"] = "https://real-url.supabase.co"
    os.environ["SUPABASE_SECRET_KEY"] = "real-key"
    db._db_instance = None
    backend = db.get_db()
    backend._client = MagicMock()
    
    mock_table = MagicMock()
    mock_table.insert().execute.side_effect = Exception("Network Error")
    backend._client.table.return_value = mock_table
    
    with pytest.raises(PersistenceError, match="Supabase create_job failed"):
        backend.create_job("job-1", "C", "T", "q", "time")

@patch("db.database.SupabaseBackend._initialize_client")
def test_supabase_jsonb_roundtrip(mock_init):
    os.environ["DATABASE_BACKEND"] = "supabase"
    os.environ["SUPABASE_URL"] = "https://real-url.supabase.co"
    os.environ["SUPABASE_SECRET_KEY"] = "real-key"
    db._db_instance = None
    backend = db.get_db()
    backend._client = MagicMock()
    
    mock_table = MagicMock()
    backend._client.table.return_value = mock_table
    
    # Simulate Supabase returning JSONB objects as python dicts/lists
    mock_table.select().eq().execute.return_value = MagicMock(data=[{
        "job_id": "job-roundtrip",
        "status": "completed",
        "result_json": {"data": "test_result"},
        "canonical_evidence_json": [{"source": "test_source"}],
        "consistency_json": {"status": "consistent"},
        "evaluation_json": {"score": 95},
        "timings_json": {"total": 500}
    }])
    
    job = backend.get_job("job-roundtrip")
    
    assert job["job_id"] == "job-roundtrip"
    assert job["status"] == "completed"
    
    # Verify that they are serialized back into JSON strings by the backend for API compatibility
    assert job["result_json"] == '{"data": "test_result"}'
    assert job["canonical_evidence_json"] == '[{"source": "test_source"}]'
    assert job["consistency_json"] == '{"status": "consistent"}'
    assert job["evaluation_json"] == '{"score": 95}'
    assert job["timings_json"] == '{"total": 500}'

