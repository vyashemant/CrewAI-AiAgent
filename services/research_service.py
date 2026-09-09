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
    
    try:
        db.create_job(
            job_id=job_id,
            company=company,
            ticker=ticker,
            status="queued",
            created_at=created_at
        )
    except Exception as e:
        logger.error(f"Failed to persist new research job {job_id}: {e}")
        from fastapi import HTTPException
        raise HTTPException(status_code=500, detail="Failed to initialize research job in database.")
        
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
        
        if isinstance(result, tuple) and len(result) >= 5:
            report, strategy_result, canonical_evidence, consistency_report, timings = result
        else:
            report = result
            strategy_result = None
            canonical_evidence = "{}"
            consistency_report = {}
            timings = {}

        if report is None:
            raise RuntimeError("Research pipeline failed to produce a valid report.")
            
        eval_score = {}
        try:
            from utils.evaluation import evaluate_research_quality
            eval_score = evaluate_research_quality(
                report.model_dump() if hasattr(report, "model_dump") else report.dict(), 
                canonical_evidence, 
                consistency_report
            )
            logger.info(f"Research Evaluation Score: {eval_score}")
        except Exception as e:
            logger.warning(f"Could not calculate evaluation score: {e}")
            
        # Serialize the Pydantic model
        if hasattr(report, "model_dump_json"):
            result_json = report.model_dump_json()
        else:
            result_json = report.json()
            
        db.update_job(
            job_id=job_id, 
            status="completed", 
            result_json=result_json,
            canonical_evidence_json=canonical_evidence,
            consistency_json=json.dumps(consistency_report) if consistency_report else None,
            evaluation_json=json.dumps(eval_score) if eval_score else None,
            timings_json=json.dumps(timings) if timings else None,
            completed_at=datetime.now(timezone.utc).isoformat()
        )
                
        logger.info(f"Background research complete for Job ID: {job_id}")
        
    except Exception as e:
        logger.error(f"Research failure for Job ID {job_id}: {str(e)}", exc_info=True)
        db.update_job(
            job_id=job_id,
            status="failed",
            error=f"Research job failed due to internal error. Diagnostics available in logs.",
            completed_at=datetime.now(timezone.utc).isoformat()
        )

def get_job_history(limit: int):
    try:
        return db.list_jobs(limit=limit)
    except Exception as e:
        logger.error(f"Failed to fetch job history: {e}")
        from fastapi import HTTPException
        raise HTTPException(status_code=500, detail="Research database temporarily unavailable.")

def get_job_status(job_id: str):
    try:
        return db.get_job(job_id)
    except Exception as e:
        logger.error(f"Failed to fetch job status for {job_id}: {e}")
        from fastapi import HTTPException
        raise HTTPException(status_code=500, detail="Research database temporarily unavailable.")

def get_research_job(job_id: str) -> Optional[Dict[str, Any]]:
    try:
        job_data = db.get_job(job_id)
    except Exception as e:
        logger.error(f"Failed to fetch research job {job_id}: {e}")
        from fastapi import HTTPException
        raise HTTPException(status_code=500, detail="Research database temporarily unavailable.")
        
    if not job_data:
        return None
        
    result = None
    if job_data.get("result_json"):
        try:
            result_dict = json.loads(job_data["result_json"])
            result = InvestmentResearchReport(**result_dict)
        except json.JSONDecodeError:
            logger.error(f"Corrupted result_json for Job ID {job_id}")
            return {
                "job_id": job_data["job_id"],
                "status": "failed",
                "result": None,
                "error": "Stored research result is corrupted.",
                "created_at": job_data["created_at"],
                "completed_at": job_data.get("completed_at")
            }
        except Exception as e:
            logger.error(f"Error parsing result for Job ID {job_id}: {e}")
            return {
                "job_id": job_data["job_id"],
                "status": "failed",
                "result": None,
                "error": "Failed to parse stored research result.",
                "created_at": job_data["created_at"],
                "completed_at": job_data.get("completed_at")
            }
        
    return {
        "job_id": job_data["job_id"],
        "status": job_data["status"],
        "result": result,
        "error": job_data.get("error"),
        "created_at": job_data["created_at"],
        "completed_at": job_data.get("completed_at")
    }
