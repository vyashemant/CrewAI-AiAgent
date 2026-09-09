import os
import sqlite3
import json
import logging
import sys
from dotenv import load_dotenv
from supabase import create_client, Client

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

def migrate():
    load_dotenv()
    
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_SECRET_KEY")
    
    if not url or not key or "your_supabase_project_url" in url:
        logger.error("Missing or invalid SUPABASE_URL or SUPABASE_SECRET_KEY in environment variables.")
        sys.exit(1)
        
    try:
        supabase: Client = create_client(url, key)
    except Exception as e:
        logger.error(f"Failed to initialize Supabase client: {e}")
        sys.exit(1)
        
    db_path = "data/research.db"
    if not os.path.exists(db_path):
        logger.info(f"No SQLite database found at {db_path}. Nothing to migrate.")
        return
        
    logger.info(f"Connecting to SQLite database at {db_path}...")
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM research_jobs")
        rows = cursor.fetchall()
    except Exception as e:
        logger.error(f"Failed to read from SQLite database: {e}")
        sys.exit(1)
    finally:
        if 'conn' in locals():
            conn.close()
            
    if not rows:
        logger.info("No records found in SQLite database.")
        return
        
    logger.info(f"Found {len(rows)} records to migrate. Starting migration...")
    
    success_count = 0
    fail_count = 0
    
    for row in rows:
        job_dict = dict(row)
        
        payload = {
            "job_id": job_dict["job_id"],
            "company": job_dict["company"],
            "ticker": job_dict["ticker"],
            "status": job_dict["status"],
            "error": job_dict.get("error"),
            "created_at": job_dict["created_at"],
            "completed_at": job_dict.get("completed_at")
        }

        # Parse JSON fields carefully
        json_fields = ["result_json", "canonical_evidence_json", "consistency_json", "evaluation_json", "timings_json"]
        for field in json_fields:
            val_str = job_dict.get(field)
            val_obj = None
            if val_str:
                try:
                    val_obj = json.loads(val_str)
                except json.JSONDecodeError:
                    logger.warning(f"Row {job_dict['job_id']}: Malformed {field}. Will migrate with null.")
            payload[field] = val_obj
        
        # Use upsert to prevent duplicate job IDs on re-runs
        try:
            supabase.table("research_jobs").upsert(payload, on_conflict="job_id").execute()
            success_count += 1
        except Exception as e:
            logger.error(f"Failed to migrate row {job_dict['job_id']}: {e}")
            fail_count += 1
            
    logger.info(f"Migration completed. Successfully migrated: {success_count}, Failed: {fail_count}.")

if __name__ == "__main__":
    migrate()
