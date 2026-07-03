import math
import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.database.session import get_db
from app.models.user import User
from app.schemas.common import Page
from app.schemas.queue import QueueCreate, QueueResponse, QueueStats, QueueUpdate
from app.services.queue_service import QueueService

router = APIRouter(prefix="/queues", tags=["Queues"])


@router.post("", response_model=QueueResponse, status_code=201)
def create_queue(payload: QueueCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return QueueService(db).create_queue(payload)


@router.get("", response_model=Page[QueueResponse])
def list_queues(
    project_id: uuid.UUID | None = None,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    items, total = QueueService(db).list_queues(project_id, offset=(page - 1) * page_size, limit=page_size)
    return Page(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=math.ceil(total / page_size) if total else 0,
    )


@router.get("/{queue_id}", response_model=QueueResponse)
def get_queue(queue_id: uuid.UUID, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return QueueService(db).get_queue(queue_id)


@router.patch("/{queue_id}", response_model=QueueResponse)
def update_queue(
    queue_id: uuid.UUID,
    payload: QueueUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return QueueService(db).update_queue(queue_id, payload)


@router.post("/{queue_id}/pause", response_model=QueueResponse)
def pause_queue(queue_id: uuid.UUID, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return QueueService(db).pause(queue_id)


@router.post("/{queue_id}/resume", response_model=QueueResponse)
def resume_queue(queue_id: uuid.UUID, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return QueueService(db).resume(queue_id)


@router.get("/{queue_id}/stats", response_model=QueueStats)
def queue_stats(queue_id: uuid.UUID, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return QueueService(db).stats(queue_id)
