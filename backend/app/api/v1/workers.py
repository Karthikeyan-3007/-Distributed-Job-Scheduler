import math
import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.database.session import get_db
from app.models.user import User
from app.schemas.common import Page
from app.schemas.job import JobResponse
from app.schemas.worker import (
    DeadLetterResponse,
    HeartbeatRequest,
    WorkerRegisterRequest,
    WorkerResponse,
)
from app.services.worker_service import DeadLetterService, WorkerService

router = APIRouter(tags=["Workers"])


@router.post("/workers", response_model=WorkerResponse, status_code=201)
def register_worker(payload: WorkerRegisterRequest, db: Session = Depends(get_db)):
    return WorkerService(db).register(payload)


@router.post("/workers/{worker_id}/heartbeat", response_model=WorkerResponse)
def heartbeat(worker_id: uuid.UUID, payload: HeartbeatRequest, db: Session = Depends(get_db)):
    return WorkerService(db).heartbeat(worker_id, payload)


@router.get("/workers", response_model=Page[WorkerResponse])
def list_workers(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    items, total = WorkerService(db).list_workers(offset=(page - 1) * page_size, limit=page_size)
    return Page(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=math.ceil(total / page_size) if total else 0,
    )


@router.get("/dead-letter-queue", response_model=Page[DeadLetterResponse])
def list_dlq(
    queue_id: uuid.UUID | None = None,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    items, total = DeadLetterService(db).list_entries(
        queue_id, offset=(page - 1) * page_size, limit=page_size
    )
    return Page(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=math.ceil(total / page_size) if total else 0,
    )


@router.post("/dead-letter-queue/{entry_id}/replay", response_model=JobResponse)
def replay_dlq_entry(
    entry_id: uuid.UUID, db: Session = Depends(get_db), user: User = Depends(get_current_user)
):
    return DeadLetterService(db).replay(entry_id)
