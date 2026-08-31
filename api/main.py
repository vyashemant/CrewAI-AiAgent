from fastapi import FastAPI, HTTPException, BackgroundTasks, status, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, field_validator
from typing import Optional, List
import logging
import uuid
import json
from datetime import datetime, timezone

from app import run_investment_research
from agents.investment_research_report import InvestmentResearchReport
import db.database as db

# Setup minimal logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="AI Investment Research API",
    description="API backend for the AI Investment Research Engine.",
    version="1.0.0"
)

# Initialize database
db.init_db()

# Basic CORS middleware for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ResearchRequest(BaseModel):
    company: str
    ticker: str

    @field_validator("company")
    @classmethod
    def validate_company(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Company cannot be empty.")
        return v.strip()

    @field_validator("ticker")
    @classmethod
    def validate_ticker(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Ticker cannot be empty.")
        return v.strip().upper()

class ResearchJobResponse(BaseModel):
    job_id: str
    status: str
    result: Optional[InvestmentResearchReport] = None
    error: Optional[str] = None
    created_at: Optional[str] = None
    completed_at: Optional[str] = None

class ResearchHistoryItem(BaseModel):
    job_id: str
    company: str
    ticker: str
    status: str
    created_at: str
    completed_at: Optional[str] = None

class ResearchHistoryResponse(BaseModel):
    research: List[ResearchHistoryItem]

def background_research_task(job_id: str, company: str, ticker: str):
    db.update_job(job_id=job_id, status="running")
            
    try:
        logger.info(f"Background research started for {company} ({ticker}), Job ID: {job_id}")
        
        result = run_investment_research(
            company=company,
            ticker=ticker
        )
        
        if isinstance(result, tuple) and len(result) >= 1:
            report = result[0]
        else:
            report = result

        if report is None:
            raise RuntimeError("Research pipeline failed to produce a valid report.")
            
        # Serialize the Pydantic model
        if hasattr(report, "model_dump_json"):
            result_json = report.model_dump_json()
        else:
            result_json = report.json()
            
        db.update_job(
            job_id=job_id, 
            status="completed", 
            result_json=result_json,
            completed_at=datetime.now(timezone.utc).isoformat()
        )
                
        logger.info(f"Background research complete for Job ID: {job_id}")
        
    except Exception as e:
        logger.error(f"Research failure for Job ID {job_id}: {str(e)}", exc_info=True)
        db.update_job(
            job_id=job_id,
            status="failed",
            error="Research job failed.",
            completed_at=datetime.now(timezone.utc).isoformat()
        )

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/api/v1/research", status_code=status.HTTP_202_ACCEPTED, response_model=ResearchJobResponse)
def research(request: ResearchRequest, background_tasks: BackgroundTasks):
    job_id = str(uuid.uuid4())
    created_at = datetime.now(timezone.utc).isoformat()
    
    db.create_job(
        job_id=job_id,
        company=request.company,
        ticker=request.ticker,
        status="queued",
        created_at=created_at
    )
        
    background_tasks.add_task(background_research_task, job_id, request.company, request.ticker)
    
    return ResearchJobResponse(
        job_id=job_id,
        status="queued",
        created_at=created_at
    )

@app.get("/api/v1/research/history", response_model=ResearchHistoryResponse)
def get_research_history(limit: int = Query(20, ge=1, le=100)):
    jobs = db.list_jobs(limit=limit)
    history_items = []
    for job in jobs:
        history_items.append(ResearchHistoryItem(
            job_id=job["job_id"],
            company=job["company"],
            ticker=job["ticker"],
            status=job["status"],
            created_at=job["created_at"],
            completed_at=job.get("completed_at")
        ))
    
    return ResearchHistoryResponse(research=history_items)

@app.get("/api/v1/research/{job_id}", response_model=ResearchJobResponse)
def get_research_status(job_id: str):
    job_data = db.get_job(job_id)
    if not job_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Research job not found."
        )
        
    result = None
    if job_data.get("result_json"):
        # Deserialize from JSON
        result_dict = json.loads(job_data["result_json"])
        result = InvestmentResearchReport(**result_dict)
        
    return ResearchJobResponse(
        job_id=job_data["job_id"],
        status=job_data["status"],
        result=result,
        error=job_data.get("error"),
        created_at=job_data["created_at"],
        completed_at=job_data.get("completed_at")
    )
