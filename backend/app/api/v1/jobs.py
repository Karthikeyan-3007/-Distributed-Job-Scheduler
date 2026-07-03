import math
import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.database.session import get_db
from app.models.enums import JobStatus
from app.models.user import User
from app.schemas.common import Page
from app.schemas.job import JobCreate, JobExecutionResponse, JobResponse
from app.services.job_service import JobService

router = APIRouter(prefix="/jobs", tags=["Jobs"])


@router.post("", response_model=JobResponse, status_code=201)
def create_job(payload: JobCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return JobService(db).create_job(payload)


@router.get("", response_model=Page[JobResponse])
def list_jobs(
    queue_id: uuid.UUID | None = None,
    status_: JobStatus | None = Query(default=None, alias="status"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    items, total = JobService(db).list_jobs(queue_id, status_, offset=(page - 1) * page_size, limit=page_size)
    return Page(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=math.ceil(total / page_size) if total else 0,
    )


@router.get("/{job_id}", response_model=JobResponse)
def get_job(job_id: uuid.UUID, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return JobService(db).get_job(job_id)


@router.post("/{job_id}/cancel", response_model=JobResponse)
def cancel_job(job_id: uuid.UUID, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return JobService(db).cancel_job(job_id)


@router.get("/{job_id}/executions", response_model=list[JobExecutionResponse])
def job_executions(job_id: uuid.UUID, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return JobService(db).executions_for_job(job_id)
