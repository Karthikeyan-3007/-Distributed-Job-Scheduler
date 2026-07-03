from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.database.session import get_db
from app.models.enums import JobStatus, WorkerStatus
from app.models.job import Job
from app.models.user import User
from app.models.worker import Worker

router = APIRouter(tags=["Metrics"])


@router.get("/health")
def health(db: Session = Depends(get_db)):
    db.execute(select(1))
    return {"status": "ok"}


@router.get("/metrics/overview")
def overview(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    def job_count(status_: JobStatus) -> int:
        stmt = select(func.count()).select_from(Job).where(Job.status == status_)
        return db.execute(stmt).scalar_one()

    total_jobs = db.execute(select(func.count()).select_from(Job)).scalar_one()
    completed = job_count(JobStatus.COMPLETED)
    failed = job_count(JobStatus.FAILED) + job_count(JobStatus.DEAD_LETTER)
    active_workers = db.execute(
        select(func.count()).select_from(Worker).where(Worker.status == WorkerStatus.ACTIVE)
    ).scalar_one()

    return {
        "total_jobs": total_jobs,
        "queued": job_count(JobStatus.QUEUED) + job_count(JobStatus.SCHEDULED),
        "running": job_count(JobStatus.RUNNING) + job_count(JobStatus.CLAIMED),
        "completed": completed,
        "failed": failed,
        "dead_letter": job_count(JobStatus.DEAD_LETTER),
        "failure_rate": round(failed / total_jobs, 4) if total_jobs else 0.0,
        "active_workers": active_workers,
    }
