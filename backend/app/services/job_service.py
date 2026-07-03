import uuid

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.enums import JobStatus, JobType
from app.models.job import Job
from app.repositories.job_execution_repository import JobExecutionRepository
from app.repositories.job_repository import JobRepository
from app.repositories.queue_repository import QueueRepository
from app.schemas.job import JobCreate


class JobService:
    def __init__(self, db: Session):
        self.db = db
        self.jobs = JobRepository(db)
        self.queues = QueueRepository(db)
        self.executions = JobExecutionRepository(db)

    def create_job(self, data: JobCreate) -> Job:
        queue = self.queues.get(data.queue_id)
        if not queue:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Queue not found")

        # Idempotency: a repeated submission with the same key returns the
        # existing job instead of creating a duplicate (safe client retries).
        if data.idempotency_key:
            from sqlalchemy import select

            existing = self.db.execute(
                select(Job).where(Job.idempotency_key == data.idempotency_key)
            ).scalar_one_or_none()
            if existing:
                return existing

        initial_status = (
            JobStatus.SCHEDULED if data.job_type in (JobType.DELAYED, JobType.SCHEDULED) else JobStatus.QUEUED
        )

        job = Job(
            queue_id=data.queue_id,
            name=data.name,
            job_type=data.job_type,
            status=initial_status,
            payload=data.payload,
            priority=data.priority,
            run_at=data.run_at,
            cron_expression=data.cron_expression,
            max_retries=data.max_retries if data.max_retries is not None else queue.max_retries,
            idempotency_key=data.idempotency_key,
        )
        self.jobs.add(job)
        self.db.commit()
        self.db.refresh(job)
        return job

    def get_job(self, job_id: uuid.UUID) -> Job:
        job = self.jobs.get(job_id)
        if not job:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Job not found")
        return job

    def list_jobs(self, queue_id: uuid.UUID | None, status_: JobStatus | None, offset: int, limit: int):
        return self.jobs.list(offset=offset, limit=limit, queue_id=queue_id, status=status_)

    def cancel_job(self, job_id: uuid.UUID) -> Job:
        job = self.get_job(job_id)
        if job.status in (JobStatus.COMPLETED, JobStatus.DEAD_LETTER, JobStatus.CANCELLED):
            raise HTTPException(status.HTTP_409_CONFLICT, f"Cannot cancel job in status {job.status}")
        job.status = JobStatus.CANCELLED
        self.db.commit()
        self.db.refresh(job)
        return job

    def executions_for_job(self, job_id: uuid.UUID):
        self.get_job(job_id)
        return self.executions.list_for_job(job_id)
