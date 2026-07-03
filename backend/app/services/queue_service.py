import uuid
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.enums import JobStatus
from app.models.job import Job
from app.models.job_execution import JobExecution
from app.models.queue import Queue
from app.models.retry_policy import RetryPolicy
from app.repositories.queue_repository import QueueRepository, RetryPolicyRepository
from app.schemas.queue import QueueCreate, QueueStats, QueueUpdate


class QueueService:
    def __init__(self, db: Session):
        self.db = db
        self.queues = QueueRepository(db)
        self.retry_policies = RetryPolicyRepository(db)

    def create_queue(self, data: QueueCreate) -> Queue:
        queue = Queue(
            project_id=data.project_id,
            name=data.name,
            priority=data.priority,
            concurrency_limit=data.concurrency_limit,
            max_retries=data.max_retries,
            timeout_seconds=data.timeout_seconds,
            visibility_timeout_seconds=data.visibility_timeout_seconds,
        )
        self.queues.add(queue)
        policy = RetryPolicy(
            queue_id=queue.id,
            strategy=data.retry_policy.strategy,
            base_delay_seconds=data.retry_policy.base_delay_seconds,
            max_delay_seconds=data.retry_policy.max_delay_seconds,
        )
        self.retry_policies.add(policy)
        self.db.commit()
        self.db.refresh(queue)
        return queue

    def get_queue(self, queue_id: uuid.UUID) -> Queue:
        queue = self.queues.get(queue_id)
        if not queue:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Queue not found")
        return queue

    def list_queues(self, project_id: uuid.UUID | None, offset: int, limit: int):
        return self.queues.list(offset=offset, limit=limit, project_id=project_id)

    def update_queue(self, queue_id: uuid.UUID, data: QueueUpdate) -> Queue:
        queue = self.get_queue(queue_id)
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(queue, field, value)
        self.db.commit()
        self.db.refresh(queue)
        return queue

    def pause(self, queue_id: uuid.UUID) -> Queue:
        queue = self.get_queue(queue_id)
        queue.is_paused = True
        self.db.commit()
        self.db.refresh(queue)
        return queue

    def resume(self, queue_id: uuid.UUID) -> Queue:
        queue = self.get_queue(queue_id)
        queue.is_paused = False
        self.db.commit()
        self.db.refresh(queue)
        return queue

    def stats(self, queue_id: uuid.UUID) -> QueueStats:
        self.get_queue(queue_id)

        def count(status_: JobStatus) -> int:
            stmt = (
                select(func.count()).select_from(Job).where(Job.queue_id == queue_id, Job.status == status_)
            )
            return self.db.execute(stmt).scalar_one()

        queued = count(JobStatus.QUEUED) + count(JobStatus.SCHEDULED)
        running = count(JobStatus.RUNNING) + count(JobStatus.CLAIMED)
        completed = count(JobStatus.COMPLETED)
        failed = count(JobStatus.FAILED)
        dead_letter = count(JobStatus.DEAD_LETTER)

        avg_stmt = (
            select(func.avg(JobExecution.duration_ms))
            .select_from(JobExecution)
            .join(Job, Job.id == JobExecution.job_id)
            .where(Job.queue_id == queue_id, JobExecution.duration_ms.is_not(None))
        )
        avg_duration = self.db.execute(avg_stmt).scalar_one()

        hour_ago = datetime.now(timezone.utc) - timedelta(hours=1)
        throughput_stmt = (
            select(func.count())
            .select_from(JobExecution)
            .join(Job, Job.id == JobExecution.job_id)
            .where(
                Job.queue_id == queue_id,
                JobExecution.completed_at.is_not(None),
                JobExecution.completed_at >= hour_ago,
            )
        )
        throughput = self.db.execute(throughput_stmt).scalar_one()

        return QueueStats(
            queue_id=queue_id,
            queued=queued,
            running=running,
            completed=completed,
            failed=failed,
            dead_letter=dead_letter,
            avg_duration_ms=float(avg_duration) if avg_duration is not None else None,
            throughput_last_hour=throughput,
        )
