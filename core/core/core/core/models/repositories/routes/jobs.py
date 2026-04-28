from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from core.database import get_db
from repositories.job_repository import JobRepository
from models.job import JobType, JobStatus
from tasks.executor import execute_word_stats, execute_word_stats_compare
from pydantic import BaseModel
from typing import Optional, Dict, Any

router = APIRouter(prefix="/jobs", tags=["jobs"])


class JobCreateRequest(BaseModel):
    type: str
    payload: Optional[Dict[str, Any]] = None


@router.post("/")
def create_job(request: JobCreateRequest, db: Session = Depends(get_db)):
    repo = JobRepository(db)
    
    if request.type not in [JobType.WORD_STATS, JobType.WORD_STATS_COMPARE]:
        raise HTTPException(status_code=400, detail=f"Unknown job type: {request.type}")
    
    job = repo.create_job(request.type, request.payload)
    
    if request.type == JobType.WORD_STATS:
        execute_word_stats.delay(job.id)
    elif request.type == JobType.WORD_STATS_COMPARE:
        execute_word_stats_compare.delay(job.id)
    
    return {"job_id": job.id, "status": job.status}


@router.get("/{job_id}")
def get_job(job_id: str, db: Session = Depends(get_db)):
    repo = JobRepository(db)
    job = repo.get_job(job_id)
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return {
        "id": job.id,
        "type": job.type,
        "status": job.status,
        "payload": job.payload,
        "result": job.result,
        "error": job.error,
        "created_at": job.created_at.isoformat() if job.created_at else None,
        "updated_at": job.updated_at.isoformat() if job.updated_at else None
    }


@router.get("/")
def list_jobs(db: Session = Depends(get_db)):
    repo = JobRepository(db)
    jobs = repo.get_all_jobs()
    
    return [
        {
            "id": job.id,
            "type": job.type,
            "status": job.status,
            "created_at": job.created_at.isoformat() if job.created_at else None
        }
        for job in jobs
    ]
