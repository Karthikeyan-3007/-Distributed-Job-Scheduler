from datetime import datetime, timezone

from sqlalchemy import select

from app.models.enums import WorkerStatus
from app.models.scheduled_job import DeadLetterQueue, ScheduledJob
from app.models.worker import Worker
from app.repositories.base import BaseRepository


class WorkerRepository(BaseRepository[Worker]):
    model = Worker

    def find_stale(self, timeout_seconds: float) -> list[Worker]:
        from datetime import timedelta

        cutoff = datetime.now(timezone.utc) - timedelta(seconds=timeout_seconds)
        stmt = select(Worker).where(
            Worker.status != WorkerStatus.CRASHED,
            Worker.status != WorkerStatus.STOPPED,
            Worker.last_heartbeat_at.is_not(None),
            Worker.last_heartbeat_at < cutoff,
        )
        return list(self.db.execute(stmt).scalars().all())


class DeadLetterRepository(BaseRepository[DeadLetterQueue]):
    model = DeadLetterQueue


class ScheduledJobRepository(BaseRepository[ScheduledJob]):
    model = ScheduledJob

    def find_due(self, now: datetime) -> list[ScheduledJob]:
        stmt = select(ScheduledJob).where(ScheduledJob.is_active.is_(True), ScheduledJob.next_run_at <= now)
        return list(self.db.execute(stmt).scalars().all())
