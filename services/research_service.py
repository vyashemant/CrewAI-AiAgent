import uuid
import logging
from datetime import datetime, timezone
import json

from typing import Tuple, Dict, Any, Optional
import db.database as db
from services.research_pipeline import run_investment_research
from agents.investment_research_report import InvestmentResearchReport

logger = logging.getLogger(__name__)

def submit_research_job(company: str, ticker: str, background_tasks) -> Tuple[str, str]:
    job_id = str(uuid.uuid4())
    created_at = datetime.now(timezone.utc).isoformat()
    
    db.create_job(
        job_id=job_id,
        company=company,
        ticker=ticker,
        status="queued",
        created_at=created_at
    )
        
    background_tasks.add_task(background_research_task, job_id, company, ticker)
    return job_id, created_at

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

def get_job_history(limit: int):
    return db.list_jobs(limit=limit)

def get_job_status(job_id: str):
    return db.get_job(job_id)

def get_research_job(job_id: str) -> Optional[Dict[str, Any]]:
    job_data = db.get_job(job_id)
    if not job_data:
        return None
        
    result = None
    if job_data.get("result_json"):
        result_dict = json.loads(job_data["result_json"])
        result = InvestmentResearchReport(**result_dict)
        
    return {
        "job_id": job_data["job_id"],
        "status": job_data["status"],
        "result": result,
        "error": job_data.get("error"),
        "created_at": job_data["created_at"],
        "completed_at": job_data.get("completed_at")
    }
