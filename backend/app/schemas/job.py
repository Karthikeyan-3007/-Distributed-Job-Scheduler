import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field, model_validator

from app.models.enums import ExecutionStatus, JobStatus, JobType


class JobCreate(BaseModel):
    queue_id: uuid.UUID
    name: str = Field(min_length=1, max_length=255)
    job_type: JobType
    payload: dict[str, Any] = Field(default_factory=dict)
    priority: int = Field(default=0, ge=0, le=100)
    run_at: datetime | None = None
    cron_expression: str | None = None
    max_retries: int | None = Field(default=None, ge=0)
    idempotency_key: str | None = None

    @model_validator(mode="after")
    def validate_type_specific_fields(self) -> "JobCreate":
        if self.job_type == JobType.RECURRING and not self.cron_expression:
            raise ValueError("cron_expression is required for recurring jobs")
        if self.job_type in (JobType.DELAYED, JobType.SCHEDULED) and not self.run_at:
            raise ValueError("run_at is required for delayed/scheduled jobs")
        return self


class JobResponse(BaseModel):
    id: uuid.UUID
    queue_id: uuid.UUID
    name: str
    job_type: JobType
    status: JobStatus
    payload: dict[str, Any]
    priority: int
    run_at: datetime | None
    cron_expression: str | None
    max_retries: int
    retry_count: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class JobExecutionResponse(BaseModel):
    id: uuid.UUID
    job_id: uuid.UUID
    worker_id: uuid.UUID | None
    attempt_number: int
    status: ExecutionStatus
    started_at: datetime | None
    completed_at: datetime | None
    duration_ms: int | None
    error_message: str | None

    model_config = {"from_attributes": True}


class JobLogResponse(BaseModel):
    id: uuid.UUID
    level: str
    message: str
    created_at: datetime

    model_config = {"from_attributes": True}
