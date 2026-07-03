import uuid
from datetime import datetime

from pydantic import BaseModel

from app.models.enums import WorkerStatus


class WorkerRegisterRequest(BaseModel):
    name: str
    hostname: str
    concurrency: int = 4


class WorkerResponse(BaseModel):
    id: uuid.UUID
    name: str
    hostname: str
    status: WorkerStatus
    concurrency: int
    last_heartbeat_at: datetime | None

    model_config = {"from_attributes": True}


class HeartbeatRequest(BaseModel):
    active_job_count: int = 0
    cpu_percent: float | None = None
    memory_mb: float | None = None


class DeadLetterResponse(BaseModel):
    id: uuid.UUID
    job_id: uuid.UUID
    queue_id: uuid.UUID
    reason: str
    payload_snapshot: dict
    replayed: bool
    created_at: datetime

    model_config = {"from_attributes": True}
