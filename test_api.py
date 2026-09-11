import pytest
import os
import tempfile
import sqlite3
from unittest.mock import patch
from datetime import datetime, timezone

# Patch the DB for testing before importing api.main
import db.database as db
db.set_testing_mode(True)

# Now it's safe to import app
from fastapi.testclient import TestClient
from api.main import app

from api.auth import get_current_user

# Set test mock mode
os.environ["DATABASE_BACKEND"] = "mock"

client = TestClient(app)
# Add valid auth token to the default client headers for existing tests
client.headers = {"Authorization": "Bearer test-token-valid"}

@pytest.fixture(autouse=True)
def setup_teardown():
    # Setup test DB (though it's created on import, we ensure it's there)
    db.init_db()
    yield
    # Teardown: clear the mock database
    db.clear_mock_db()

def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_research_endpoint_validation_empty_body():
    response = client.post("/api/v1/research", json={})
    assert response.status_code == 422  # FastAPI validation error

def test_research_endpoint_validation_missing_fields():
    response = client.post("/api/v1/research", json={"company": "Apple Inc."})
    assert response.status_code == 422

def test_research_endpoint_validation_empty_strings():
    response = client.post("/api/v1/research", json={"company": "   ", "ticker": ""})
    assert response.status_code == 422

def test_research_endpoint_success(monkeypatch):
    # Mock the run_investment_research function
    def mock_run_investment_research(company, ticker):
        from agents.investment_research_report import (
            InvestmentResearchReport,
            MarketSnapshot,
            FinancialSummary,
            FinancialMetrics,
            SpecialistReports,
            DataSources,
            EvidenceRegistry,
            EvidenceItem
        )
        from agents.investment_strategist import InvestmentStrategy
        
        # Verify validation happened
        assert company == "Apple Inc."
        assert ticker == "AAPL"
        
        report = InvestmentResearchReport(
            company=company,
            ticker=ticker,
            research_date="2026-08-27",
            market_snapshot=MarketSnapshot(),
            financial_summary=FinancialSummary(),
            financial_metrics=FinancialMetrics(),
            news="Mock news",
            specialist_reports=SpecialistReports(
                financial_analyst="Mock FA",
                market_news_analyst="Mock MN",
                valuation_analyst="Mock VA",
                risk_analyst="Mock RA"
            ),
            investment_strategy=InvestmentStrategy(
                recommendation="BUY",
                confidence="HIGH",
                investment_thesis="Mock thesis",
                company_quality="Mock quality",
                valuation_view="Mock valuation",
                fundamental_assessment="Mock fundamental",
                market_and_news_assessment="Mock market",
                valuation_assessment="Mock valuation assessment",
                risk_assessment="Mock risk",
                bull_case="Mock bull",
                base_case="Mock base",
                bear_case="Mock bear",
                key_catalysts=["Cat1"],
                key_risks=["Risk1"],
                thesis_change_triggers=["Trigger1"],
                evidence_summary="Mock evidence",
                information_limitations="Mock limits"
            ),
            data_sources=DataSources(),
            evidence_registry=EvidenceRegistry(
                evidence=[
                    EvidenceItem(
                        evidence_id="MKT-001",
                        evidence_type="market_data",
                        source="System",
                        claim="Mock claim"
                    )
                ]
            )
        )
        # Returning exactly what run_investment_research now returns (5 items)
        return (report, None, "{}", {}, {})

    monkeypatch.setattr("services.research_service.run_investment_research", mock_run_investment_research)

    response = client.post(
        "/api/v1/research", 
        json={"company": " Apple Inc. ", "ticker": " aapl "}
    )
    
    assert response.status_code == 202
    data = response.json()
    assert "job_id" in data
    assert data["status"] in ["queued", "running", "completed"]
    
    job_id = data["job_id"]
    
    # Check status endpoint
    status_response = client.get(f"/api/v1/research/{job_id}")
    assert status_response.status_code == 200
    status_data = status_response.json()
    
    # In a TestClient, BackgroundTasks run synchronously after the response is sent.
    # Therefore, the job should be 'completed' when we fetch it.
    assert status_data["status"] == "completed"
    assert status_data["result"]["company"] == "Apple Inc."
    assert status_data["result"]["ticker"] == "AAPL"
    assert status_data["result"]["investment_strategy"]["recommendation"] == "BUY"
    assert "evidence_registry" in status_data["result"]
    assert len(status_data["result"]["evidence_registry"]["evidence"]) == 1
    assert status_data["result"]["evidence_registry"]["evidence"][0]["evidence_id"] == "MKT-001"

    # Test history endpoint
    history_response = client.get("/api/v1/research/history")
    assert history_response.status_code == 200
    history_data = history_response.json()
    assert len(history_data["research"]) == 1
    assert history_data["research"][0]["job_id"] == job_id
    assert history_data["research"][0]["company"] == "Apple Inc."
    assert history_data["research"][0]["ticker"] == "AAPL"
    # Full report shouldn't be in history
    assert "result" not in history_data["research"][0]
    
    # Test persistence (re-retrieve directly from DB to simulate restart)
    db_job = db.get_job(job_id)
    assert db_job is not None
    assert db_job["job_id"] == job_id
    assert db_job["status"] == "completed"

def test_research_endpoint_failure(monkeypatch):
    def mock_run_investment_research_failure(company, ticker):
        raise RuntimeError("Mock failure")

    monkeypatch.setattr("services.research_service.run_investment_research", mock_run_investment_research_failure)

    response = client.post(
        "/api/v1/research", 
        json={"company": "Apple Inc.", "ticker": "AAPL"}
    )
    
    assert response.status_code == 202
    job_id = response.json()["job_id"]
    
    status_response = client.get(f"/api/v1/research/{job_id}")
    assert status_response.status_code == 200
    status_data = status_response.json()
    
    assert status_data["status"] == "failed"
    assert status_data["error"] == "Research job failed due to internal error. Diagnostics available in logs."

def test_research_endpoint_unknown_job():
    response = client.get("/api/v1/research/invalid-uuid-1234")
    assert response.status_code == 404
    assert response.json()["detail"] == "Research job not found."

def test_history_limits():
    # Insert 25 jobs directly into db
    import uuid
    from datetime import datetime, timezone, timedelta
    base_time = datetime.now(timezone.utc)
    for i in range(25):
        job_id = f"job-{i}"
        created_at = (base_time + timedelta(seconds=i)).isoformat()
        db.create_job(job_id, f"Company {i}", "TCK", "completed", created_at, user_id="test-user-id")
        
    # Default limit is 20
    resp = client.get("/api/v1/research/history")
    assert resp.status_code == 200
    assert len(resp.json()["research"]) == 20
    
    # Limit 2
    resp = client.get("/api/v1/research/history?limit=2")
    assert resp.status_code == 200
    assert len(resp.json()["research"]) == 2
    
    # Limit 100 (should return all 25)
    resp = client.get("/api/v1/research/history?limit=100")
    assert resp.status_code == 200
    assert len(resp.json()["research"]) == 25
    
    # Limit 0 (invalid)
    resp = client.get("/api/v1/research/history?limit=0")
    assert resp.status_code == 422
    
    # Limit 101 (invalid)
    resp = client.get("/api/v1/research/history?limit=101")
    assert resp.status_code == 422

def test_history_ordering():
    now_str = datetime.now(timezone.utc).isoformat()
    db.create_job("job-1", "A", "T", "queued", "2026-08-01T10:00:00", user_id="test-user-id")
    db.create_job("job-2", "B", "T", "queued", "2026-08-03T10:00:00", user_id="test-user-id")
    db.create_job("job-3", "C", "T", "queued", "2026-08-02T10:00:00", user_id="test-user-id")
    
    response = client.get("/api/v1/research/history?limit=3")
    assert response.status_code == 200
    history = response.json()["research"]
    
    assert history[0]["job_id"] == "job-2"
    assert history[1]["job_id"] == "job-3"
    assert history[2]["job_id"] == "job-1"

def test_api_database_failure_history():
    with patch("db.database.list_jobs", side_effect=Exception("DB connection lost")):
        response = client.get("/api/v1/research/history")
        assert response.status_code == 500
        assert "temporarily unavailable" in response.json()["detail"]

def test_api_database_failure_get_job():
    with patch("db.database.get_job", side_effect=Exception("DB connection lost")):
        response = client.get("/api/v1/research/job-123")
        assert response.status_code == 500
        assert "temporarily unavailable" in response.json()["detail"]

def test_persistence_simulate_restart(monkeypatch):
    import json
    
    # 1. Create a job directly in the DB mimicking a completed run
    job_id = "persistent-job-123"
    db.create_job(job_id, "Test Restart", "TEST", "running", "2026-08-31T10:00:00", user_id="test-user-id")
    
    mock_report = {
        "company": "Test Restart",
        "ticker": "TEST",
        "research_date": "2026-08-31",
        "market_snapshot": {},
        "financial_summary": {},
        "financial_metrics": {},
        "news": "Mock",
        "specialist_reports": {
            "financial_analyst": "",
            "market_news_analyst": "",
            "valuation_analyst": "",
            "risk_analyst": ""
        },
        "investment_strategy": {
            "recommendation": "BUY",
            "confidence": "HIGH",
            "investment_thesis": "",
            "company_quality": "",
            "valuation_view": "",
            "fundamental_assessment": "",
            "market_and_news_assessment": "",
            "valuation_assessment": "",
            "risk_assessment": "",
            "bull_case": "",
            "base_case": "",
            "bear_case": "",
            "key_catalysts": [],
            "key_risks": [],
            "thesis_change_triggers": [],
            "evidence_summary": "",
            "information_limitations": ""
        },
        "data_sources": {}
    }
    
    db.update_job(job_id, "completed", json.dumps(mock_report), None, "2026-08-31T10:01:00")
    
    # 3 & 4. Initialize a completely new TestClient instance to simulate restart
    new_client = TestClient(app)
    new_client.headers = {"Authorization": "Bearer test-token-valid"}
    
    # 5. Retrieve the job
    resp = new_client.get(f"/api/v1/research/{job_id}")
    
    # 6. Verify result is still available
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "completed"
    assert data["result"]["company"] == "Test Restart"
    assert data["result"]["ticker"] == "TEST"
    assert data["result"]["investment_strategy"]["recommendation"] == "BUY"

def test_persistence_malformed_json():
    # Insert malformed json directly into DB
    job_id = "malformed-job-123"
    db.create_job(job_id, "Malformed", "MAL", "queued", "2026-08-31T10:00:00", user_id="test-user-id")
    db.update_job(job_id, "running")
    db.update_job(job_id, "completed", "{ invalid_json: 123 ", None, "2026-08-31T10:01:00")
    
    # Retrieve should fail safely or return None for result
    
    # Actually let's test the endpoint
    response = client.get(f"/api/v1/research/{job_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "failed"
    assert data["error"] == "Stored research result is corrupted."

def test_lifecycle_failure_running(monkeypatch):
    original_update = db.update_job
    def mock_update_job(job_id, status, **kwargs):
        if status == "running":
            raise db.PersistenceError("Mock DB down")
        return original_update(job_id, status, **kwargs)
        
    monkeypatch.setattr("db.database.update_job", mock_update_job)
    
    def mock_run(*args, **kwargs):
        raise RuntimeError("Research should not run")
    monkeypatch.setattr("services.research_service.run_investment_research", mock_run)

    response = client.post("/api/v1/research", json={"company": "Apple Inc.", "ticker": "AAPL"})
    job_id = response.json()["job_id"]
    
    status_response = client.get(f"/api/v1/research/{job_id}")
    assert status_response.json()["status"] == "queued"

def test_lifecycle_failure_completed(monkeypatch):
    original_update = db.update_job
    def mock_update_job(job_id, status, **kwargs):
        if status == "completed":
            raise db.PersistenceError("Mock DB down")
        return original_update(job_id, status, **kwargs)
        
    monkeypatch.setattr("db.database.update_job", mock_update_job)
    
    def mock_run(*args, **kwargs):
        from agents.investment_research_report import InvestmentResearchReport, MarketSnapshot, FinancialSummary, FinancialMetrics, SpecialistReports, InvestmentStrategy, DataSources, EvidenceRegistry
        report = InvestmentResearchReport(
            company="Apple Inc.", ticker="AAPL", research_date="2026-08-27",
            market_snapshot=MarketSnapshot(), financial_summary=FinancialSummary(),
            financial_metrics=FinancialMetrics(), news="Mock",
            specialist_reports=SpecialistReports(financial_analyst="", market_news_analyst="", valuation_analyst="", risk_analyst=""),
            investment_strategy=InvestmentStrategy(recommendation="BUY", confidence="HIGH", investment_thesis="", company_quality="", valuation_view="", fundamental_assessment="", market_and_news_assessment="", valuation_assessment="", risk_assessment="", bull_case="", base_case="", bear_case="", key_catalysts=[], key_risks=[], thesis_change_triggers=[], evidence_summary="", information_limitations=""),
            data_sources=DataSources(), evidence_registry=EvidenceRegistry(evidence=[])
        )
        return (report, None, "{}", {}, {})
    monkeypatch.setattr("services.research_service.run_investment_research", mock_run)

    response = client.post("/api/v1/research", json={"company": "Apple Inc.", "ticker": "AAPL"})
    job_id = response.json()["job_id"]
    
    status_response = client.get(f"/api/v1/research/{job_id}")
    assert status_response.json()["status"] == "running"

def test_lifecycle_failure_failed(monkeypatch):
    original_update = db.update_job
    def mock_update_job(job_id, status, **kwargs):
        if status == "failed":
            raise db.PersistenceError("Mock DB down")
        return original_update(job_id, status, **kwargs)
        
    monkeypatch.setattr("db.database.update_job", mock_update_job)
    
    def mock_run(*args, **kwargs):
        raise RuntimeError("Research failed")
    monkeypatch.setattr("services.research_service.run_investment_research", mock_run)

    response = client.post("/api/v1/research", json={"company": "Apple Inc.", "ticker": "AAPL"})
    job_id = response.json()["job_id"]
    
    status_response = client.get(f"/api/v1/research/{job_id}")
    assert status_response.json()["status"] == "running"

def test_invalid_transitions():
    import pytest
    from db.database import PersistenceError
    db.create_job("tr-1", "C", "T", "queued", "2026-08-31T10:00:00", user_id="test-user-id")
    
    with pytest.raises(PersistenceError, match="Invalid state transition from queued to completed"):
        db.update_job("tr-1", "completed")
        
    with pytest.raises(PersistenceError, match="Invalid state transition from queued to failed"):
        db.update_job("tr-1", "failed")

    # Move to completed
    db.update_job("tr-1", "running")
    db.update_job("tr-1", "completed")
    
    with pytest.raises(PersistenceError, match="Invalid state transition from completed to running"):
        db.update_job("tr-1", "running")
        
    with pytest.raises(PersistenceError, match="Invalid state transition from completed to failed"):
        db.update_job("tr-1", "failed")

    db.create_job("tr-2", "C", "T", "queued", "2026-08-31T10:00:00", user_id="test-user-id")
    db.update_job("tr-2", "running")
    db.update_job("tr-2", "failed")
    
    with pytest.raises(PersistenceError, match="Invalid state transition from failed to running"):
        db.update_job("tr-2", "running")

    with pytest.raises(PersistenceError, match="Invalid state transition from failed to completed"):
        db.update_job("tr-2", "completed")

    # verify records are unchanged after rejected transitions
    assert db.get_job("tr-1")["status"] == "completed"
    assert db.get_job("tr-2")["status"] == "failed"

def test_timestamp_lifecycle_success(monkeypatch):
    def mock_run(*args, **kwargs):
        from agents.investment_research_report import InvestmentResearchReport, MarketSnapshot, FinancialSummary, FinancialMetrics, SpecialistReports, InvestmentStrategy, DataSources, EvidenceRegistry
        report = InvestmentResearchReport(
            company="Apple Inc.", ticker="AAPL", research_date="2026-08-27",
            market_snapshot=MarketSnapshot(), financial_summary=FinancialSummary(),
            financial_metrics=FinancialMetrics(), news="Mock",
            specialist_reports=SpecialistReports(financial_analyst="", market_news_analyst="", valuation_analyst="", risk_analyst=""),
            investment_strategy=InvestmentStrategy(recommendation="BUY", confidence="HIGH", investment_thesis="", company_quality="", valuation_view="", fundamental_assessment="", market_and_news_assessment="", valuation_assessment="", risk_assessment="", bull_case="", base_case="", bear_case="", key_catalysts=[], key_risks=[], thesis_change_triggers=[], evidence_summary="", information_limitations=""),
            data_sources=DataSources(), evidence_registry=EvidenceRegistry(evidence=[])
        )
        return (report, None, "{}", {}, {})
    monkeypatch.setattr("services.research_service.run_investment_research", mock_run)

    response = client.post("/api/v1/research", json={"company": "Apple Inc.", "ticker": "AAPL"})
    data = response.json()
    job_id = data["job_id"]
    original_created_at = data["created_at"]
    
    job_record = db.get_job(job_id)
    assert job_record["status"] == "completed"
    assert job_record["created_at"] == original_created_at
    
    created_at = datetime.fromisoformat(job_record["created_at"])
    completed_at = datetime.fromisoformat(job_record["completed_at"])
    assert completed_at >= created_at

def test_timestamp_lifecycle_failure(monkeypatch):
    def mock_run(*args, **kwargs):
        raise RuntimeError("Research failed")
    monkeypatch.setattr("services.research_service.run_investment_research", mock_run)

    response = client.post("/api/v1/research", json={"company": "Apple Inc.", "ticker": "AAPL"})
    data = response.json()
    job_id = data["job_id"]
    original_created_at = data["created_at"]
    
    job_record = db.get_job(job_id)
    assert job_record["status"] == "failed"
    assert job_record["created_at"] == original_created_at
    
    created_at = datetime.fromisoformat(job_record["created_at"])
    completed_at = datetime.fromisoformat(job_record["completed_at"])
    assert completed_at >= created_at

def test_auth_missing_header():
    # Remove default auth header
    client.headers.pop("Authorization", None)
    response = client.get("/health")
    # /health doesn't have auth on it, let's test /api/v1/research/history
    response = client.get("/api/v1/research/history")
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"
    
    # Restore header
    client.headers["Authorization"] = "Bearer test-token-valid"

def test_auth_invalid_header():
    client.headers["Authorization"] = "Bearer invalid-token"
    response = client.get("/api/v1/research/history")
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid authentication credentials"
    
    # Restore header
    client.headers["Authorization"] = "Bearer test-token-valid"

def test_auth_isolation(monkeypatch):
    # Mock research run so we don't need real results
    def mock_run(*args, **kwargs):
        raise RuntimeError("Should not be called")
    monkeypatch.setattr("services.research_service.run_investment_research", mock_run)

    # User A creates a job
    client.headers["Authorization"] = "Bearer test-token-valid"
    response_a = client.post("/api/v1/research", json={"company": "User A Corp", "ticker": "AAA"})
    assert response_a.status_code == 202
    job_id_a = response_a.json()["job_id"]
    
    # User B creates a job
    client.headers["Authorization"] = "Bearer test-token-valid-user-b"
    response_b = client.post("/api/v1/research", json={"company": "User B Corp", "ticker": "BBB"})
    assert response_b.status_code == 202
    job_id_b = response_b.json()["job_id"]
    
    # User A cannot retrieve User B's job
    client.headers["Authorization"] = "Bearer test-token-valid"
    status_a_for_b = client.get(f"/api/v1/research/{job_id_b}")
    assert status_a_for_b.status_code == 404
    
    # User A's history only contains User A's jobs
    hist_a = client.get("/api/v1/research/history")
    assert hist_a.status_code == 200
    hist_a_jobs = [j["job_id"] for j in hist_a.json()["research"]]
    assert job_id_a in hist_a_jobs
    assert job_id_b not in hist_a_jobs
    
    # User B's history only contains User B's jobs
    client.headers["Authorization"] = "Bearer test-token-valid-user-b"
    hist_b = client.get("/api/v1/research/history")
    assert hist_b.status_code == 200
    hist_b_jobs = [j["job_id"] for j in hist_b.json()["research"]]
    assert job_id_b in hist_b_jobs
    assert job_id_a not in hist_b_jobs
    
    # Restore header
    client.headers["Authorization"] = "Bearer test-token-valid"
