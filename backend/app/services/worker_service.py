import uuid
from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.enums import JobStatus, WorkerStatus
from app.models.worker import Worker, WorkerHeartbeat
from app.repositories.worker_repository import DeadLetterRepository, WorkerRepository
from app.schemas.worker import HeartbeatRequest, WorkerRegisterRequest


class WorkerService:
    def __init__(self, db: Session):
        self.db = db
        self.workers = WorkerRepository(db)

    def register(self, data: WorkerRegisterRequest) -> Worker:
        worker = Worker(
            name=data.name,
            hostname=data.hostname,
            concurrency=data.concurrency,
            status=WorkerStatus.ACTIVE,
            last_heartbeat_at=datetime.now(timezone.utc),
        )
        self.workers.add(worker)
        self.db.commit()
        self.db.refresh(worker)
        return worker

    def heartbeat(self, worker_id: uuid.UUID, data: HeartbeatRequest) -> Worker:
        worker = self.workers.get(worker_id)
        if not worker:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Worker not found")
        worker.last_heartbeat_at = datetime.now(timezone.utc)
        worker.status = WorkerStatus.ACTIVE if data.active_job_count > 0 else WorkerStatus.IDLE
        self.db.add(
            WorkerHeartbeat(
                worker_id=worker.id,
                active_job_count=data.active_job_count,
                cpu_percent=data.cpu_percent,
                memory_mb=data.memory_mb,
            )
        )
        self.db.commit()
        self.db.refresh(worker)
        return worker

    def list_workers(self, offset: int, limit: int):
        return self.workers.list(offset=offset, limit=limit)

    def mark_stale_as_crashed(self, timeout_seconds: float) -> list[Worker]:
        """
        Called periodically (by the scheduler tick) so the dashboard
        reflects reality even if a worker died without a clean shutdown.
        Jobs it was holding are recovered separately by claim_jobs(),
        which treats any job past its visibility timeout as reclaimable
        regardless of what the owning worker's status says.
        """
        stale = self.workers.find_stale(timeout_seconds)
        for worker in stale:
            worker.status = WorkerStatus.CRASHED
        if stale:
            self.db.commit()
        return stale


class DeadLetterService:
    def __init__(self, db: Session):
        self.db = db
        self.dlq = DeadLetterRepository(db)

    def list_entries(self, queue_id: uuid.UUID | None, offset: int, limit: int):
        return self.dlq.list(offset=offset, limit=limit, queue_id=queue_id)

    def replay(self, entry_id: uuid.UUID):
        from app.models.job import Job

        entry = self.dlq.get(entry_id)
        if not entry:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Dead letter entry not found")
        job = self.db.get(Job, entry.job_id)
        if not job:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Original job no longer exists")
        job.status = JobStatus.QUEUED
        job.retry_count = 0
        job.run_at = None
        entry.replayed = True
        self.db.commit()
        self.db.refresh(job)
        return job
