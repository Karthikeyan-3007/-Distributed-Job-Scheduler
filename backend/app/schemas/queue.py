import uuid
from datetime import datetime

from pydantic import BaseModel, Field

from app.models.enums import RetryStrategy


class RetryPolicyIn(BaseModel):
    strategy: RetryStrategy = RetryStrategy.EXPONENTIAL
    base_delay_seconds: int = Field(default=5, gt=0)
    max_delay_seconds: int = Field(default=300, gt=0)


class RetryPolicyResponse(RetryPolicyIn):
    id: uuid.UUID
    model_config = {"from_attributes": True}


class QueueCreate(BaseModel):
    project_id: uuid.UUID
    name: str = Field(min_length=1, max_length=255)
    priority: int = Field(default=0, ge=0, le=100)
    concurrency_limit: int = Field(default=5, gt=0)
    max_retries: int = Field(default=3, ge=0)
    timeout_seconds: int = Field(default=300, gt=0)
    visibility_timeout_seconds: int = Field(default=60, gt=0)
    retry_policy: RetryPolicyIn = RetryPolicyIn()


class QueueUpdate(BaseModel):
    priority: int | None = Field(default=None, ge=0, le=100)
    concurrency_limit: int | None = Field(default=None, gt=0)
    max_retries: int | None = Field(default=None, ge=0)
    timeout_seconds: int | None = Field(default=None, gt=0)
    visibility_timeout_seconds: int | None = Field(default=None, gt=0)
    is_paused: bool | None = None


class QueueResponse(BaseModel):
    id: uuid.UUID
    project_id: uuid.UUID
    name: str
    priority: int
    concurrency_limit: int
    max_retries: int
    timeout_seconds: int
    visibility_timeout_seconds: int
    is_paused: bool
    created_at: datetime
    retry_policy: RetryPolicyResponse | None = None

    model_config = {"from_attributes": True}


class QueueStats(BaseModel):
    queue_id: uuid.UUID
    queued: int
    running: int
    completed: int
    failed: int
    dead_letter: int
    avg_duration_ms: float | None
    throughput_last_hour: int
