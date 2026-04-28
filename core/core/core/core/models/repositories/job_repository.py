from sqlalchemy.orm import Session
from models.job import Job, JobStatus
from typing import Optional, List
import uuid


class JobRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_job(self, job_type: str, payload: dict = None) -> Job:
        job = Job(
            id=str(uuid.uuid4()),
            type=job_type,
            status=JobStatus.PENDING,
            payload=payload
        )
        self.db.add(job)
        self.db.commit()
        self.db.refresh(job)
        return job

    def get_job(self, job_id: str) -> Optional[Job]:
        return self.db.query(Job).filter(Job.id == job_id).first()

    def get_all_jobs(self) -> List[Job]:
        return self.db.query(Job).order_by(Job.created_at.desc()).all()

    def update_job_status(self, job_id: str, status: str, result: dict = None, error: str = None) -> Optional[Job]:
        job = self.get_job(job_id)
        if job:
            job.status = status
            if result is not None:
                job.result = result
            if error is not None:
                job.error = error
            self.db.commit()
            self.db.refresh(job)
        return job
