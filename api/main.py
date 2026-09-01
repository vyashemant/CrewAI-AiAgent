from fastapi import FastAPI, HTTPException, BackgroundTasks, status, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, field_validator
from typing import Optional, List
import logging
from contextlib import asynccontextmanager

from agents.investment_research_report import InvestmentResearchReport
from services.research_service import submit_research_job, get_job_history, get_research_job

# Setup minimal logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    import db.database as db
    db.init_db()
    yield

app = FastAPI(
    title="AI Investment Research API",
    description="API backend for the AI Investment Research Engine.",
    version="1.0.0",
    lifespan=lifespan
)

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

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/api/v1/research", status_code=status.HTTP_202_ACCEPTED, response_model=ResearchJobResponse)
def research(request: ResearchRequest, background_tasks: BackgroundTasks):
    job_id, created_at = submit_research_job(
        company=request.company, 
        ticker=request.ticker, 
        background_tasks=background_tasks
    )
    
    return ResearchJobResponse(
        job_id=job_id,
        status="queued",
        created_at=created_at
    )

@app.get("/api/v1/research/history", response_model=ResearchHistoryResponse)
def get_research_history_route(limit: int = Query(20, ge=1, le=100)):
    jobs = get_job_history(limit=limit)
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
def get_research_status_route(job_id: str):
    job_data = get_research_job(job_id)
    if not job_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Research job not found."
        )
        
    return ResearchJobResponse(
        job_id=job_data["job_id"],
        status=job_data["status"],
        result=job_data.get("result"),
        error=job_data.get("error"),
        created_at=job_data["created_at"],
        completed_at=job_data.get("completed_at")
    )
