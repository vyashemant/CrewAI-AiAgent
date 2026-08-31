import pytest
import os
import tempfile
import sqlite3

# Patch the DB_PATH before importing api.main
import db.database as db
temp_dir = tempfile.mkdtemp()
temp_db_path = os.path.join(temp_dir, "test_research.db")
db.DB_PATH = temp_db_path
db.DB_DIR = temp_dir

# Now it's safe to import app because db.init_db() will use temp_db_path
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_teardown():
    # Setup test DB (though it's created on import, we ensure it's there)
    db.init_db(temp_db_path)
    yield
    # Teardown: clear the table after each test
    with sqlite3.connect(temp_db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM research_jobs")
        conn.commit()

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
        # Returning exactly what app.py returns
        return (report, None, {})

    monkeypatch.setattr("api.main.run_investment_research", mock_run_investment_research)

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

    monkeypatch.setattr("api.main.run_investment_research", mock_run_investment_research_failure)

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
    assert "error" in status_data
    assert status_data["error"] == "Research job failed."

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
        db.create_job(job_id, f"Company {i}", "TCK", "completed", created_at)
        
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
    # Insert 3 jobs with out-of-order timestamps
    db.create_job("job-1", "A", "A", "completed", "2026-08-30T10:00:00")
    db.create_job("job-2", "B", "B", "completed", "2026-08-31T10:00:00")
    db.create_job("job-3", "C", "C", "completed", "2026-08-29T10:00:00")
    
    resp = client.get("/api/v1/research/history")
    assert resp.status_code == 200
    history = resp.json()["research"]
    assert len(history) == 3
    
    # Should be newest first
    assert history[0]["job_id"] == "job-2"
    assert history[1]["job_id"] == "job-1"
    assert history[2]["job_id"] == "job-3"

def test_persistence_simulate_restart(monkeypatch):
    import json
    
    # 1. Create a job directly in the DB mimicking a completed run
    job_id = "persistent-job-123"
    db.create_job(job_id, "Test Restart", "TEST", "running", "2026-08-31T10:00:00")
    
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
    
    # 5. Retrieve the job
    resp = new_client.get(f"/api/v1/research/{job_id}")
    
    # 6. Verify result is still available
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "completed"
    assert data["result"]["company"] == "Test Restart"
    assert data["result"]["ticker"] == "TEST"
    assert data["result"]["investment_strategy"]["recommendation"] == "BUY"
