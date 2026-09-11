import pytest
import os
from datetime import datetime, timezone, timedelta
from unittest.mock import patch, MagicMock

import db.database as db
from services.research_service import find_stale_running_jobs, submit_research_job, background_research_task

@pytest.fixture(autouse=True)
def setup_mock_db():
    db.set_testing_mode(True)
    db.init_db()
    db.clear_mock_db()
    yield
    db.clear_mock_db()
    db.set_testing_mode(False)

def test_stale_recovery_running_below_timeout():
    now = datetime.now(timezone.utc)
    started_at = (now - timedelta(seconds=1000)).isoformat() # default timeout is 3600
    db.create_job("job1", "Company", "CMP", "queued", now.isoformat())
    db.update_job("job1", "running", started_at=started_at)
    
    find_stale_running_jobs()
    
    job = db.get_job("job1")
    assert job["status"] == "running"

def test_stale_recovery_running_above_timeout():
    now = datetime.now(timezone.utc)
    created_at = (now - timedelta(seconds=4000)).isoformat()
    started_at = (now - timedelta(seconds=3700)).isoformat()
    
    db.create_job("job1", "Company", "CMP", "queued", created_at)
    db.update_job("job1", "running", started_at=started_at)
    
    find_stale_running_jobs()
    
    job = db.get_job("job1")
    assert job["status"] == "failed"
    assert job["error"] == "Research job timed out before completion."
    assert job["created_at"] == created_at
    assert job["started_at"] == started_at
    assert job["completed_at"] is not None

def test_stale_recovery_idempotent():
    now = datetime.now(timezone.utc)
    started_at = (now - timedelta(seconds=3700)).isoformat()
    
    db.create_job("job1", "Company", "CMP", "queued", now.isoformat())
    db.update_job("job1", "running", started_at=started_at)
    
    find_stale_running_jobs()
    job_first = db.get_job("job1")
    
    # second pass
    find_stale_running_jobs()
    job_second = db.get_job("job1")
    
    assert job_first["status"] == "failed"
    assert job_second["status"] == "failed"
    assert job_first["completed_at"] == job_second["completed_at"]

def test_completed_job_never_stale():
    now = datetime.now(timezone.utc)
    started_at = (now - timedelta(seconds=4000)).isoformat()
    completed_at = (now - timedelta(seconds=3900)).isoformat()
    
    db.create_job("job1", "Company", "CMP", "queued", now.isoformat())
    db.update_job("job1", "running", started_at=started_at)
    db.update_job("job1", "completed", completed_at=completed_at)
    
    find_stale_running_jobs()
    
    job = db.get_job("job1")
    assert job["status"] == "completed"

def test_failed_job_never_stale():
    now = datetime.now(timezone.utc)
    started_at = (now - timedelta(seconds=4000)).isoformat()
    completed_at = (now - timedelta(seconds=3900)).isoformat()
    
    db.create_job("job1", "Company", "CMP", "queued", now.isoformat())
    db.update_job("job1", "running", started_at=started_at)
    db.update_job("job1", "failed", completed_at=completed_at)
    
    find_stale_running_jobs()
    
    job = db.get_job("job1")
    assert job["status"] == "failed"

def test_multiple_stale_jobs():
    now = datetime.now(timezone.utc)
    db.create_job("job1", "Company", "CMP", "queued", now.isoformat())
    db.update_job("job1", "running", started_at=(now - timedelta(seconds=3700)).isoformat())
    
    db.create_job("job2", "Company2", "CMP2", "queued", now.isoformat())
    db.update_job("job2", "running", started_at=(now - timedelta(seconds=3800)).isoformat())
    
    db.create_job("job3", "Company3", "CMP3", "queued", now.isoformat())
    db.update_job("job3", "running", started_at=(now - timedelta(seconds=1000)).isoformat())
    
    find_stale_running_jobs()
    
    assert db.get_job("job1")["status"] == "failed"
    assert db.get_job("job2")["status"] == "failed"
    assert db.get_job("job3")["status"] == "running"

@patch("db.database.list_jobs")
def test_database_failure_lookup(mock_list_jobs):
    mock_list_jobs.side_effect = db.PersistenceError("DB down")
    with pytest.raises(db.PersistenceError):
        find_stale_running_jobs()

def test_database_failure_update():
    now = datetime.now(timezone.utc)
    db.create_job("job1", "Company", "CMP", "queued", now.isoformat())
    db.update_job("job1", "running", started_at=(now - timedelta(seconds=3700)).isoformat())
    
    with patch("db.database.update_job") as mock_update_job:
        mock_update_job.side_effect = db.PersistenceError("DB update failed")
        
        with pytest.raises(db.PersistenceError):
            find_stale_running_jobs()

def test_configurable_timeout_respected():
    now = datetime.now(timezone.utc)
    started_at = (now - timedelta(seconds=100)).isoformat()
    db.create_job("job1", "Company", "CMP", "queued", now.isoformat())
    db.update_job("job1", "running", started_at=started_at)
    
    with patch("services.research_service.RESEARCH_JOB_TIMEOUT_SECONDS", 50):
        find_stale_running_jobs()
        
    job = db.get_job("job1")
    assert job["status"] == "failed"

def test_utc_timestamp_handling():
    now = datetime.now(timezone.utc)
    started_at = (now - timedelta(seconds=3700)).isoformat()
    db.create_job("job1", "Company", "CMP", "queued", now.isoformat())
    db.update_job("job1", "running", started_at=started_at)
    
    find_stale_running_jobs()
    job = db.get_job("job1")
    
    assert job["completed_at"].endswith("+00:00")
