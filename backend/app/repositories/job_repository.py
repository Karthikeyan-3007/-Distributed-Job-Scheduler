import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.enums import JobStatus
from app.models.job import Job
from app.repositories.base import BaseRepository


class JobRepository(BaseRepository[Job]):
    model = Job

    def __init__(self, db: Session):
        super().__init__(db)

    def count_running(self, queue_id: uuid.UUID) -> int:
        stmt = (
            select(func.count())
            .select_from(Job)
            .where(Job.queue_id == queue_id, Job.status == JobStatus.RUNNING)
        )
        return self.db.execute(stmt).scalar_one()

    def claim_jobs(
        self, queue_id: uuid.UUID, worker_id: uuid.UUID, max_jobs: int, visibility_timeout_seconds: int
    ) -> list[Job]:
        """
        Atomically claims up to `max_jobs` ready jobs from a queue.

        Safety argument (why concurrent workers can never double-claim):

        1. `SELECT ... FOR UPDATE SKIP LOCKED` takes row-level write locks
           on the candidate rows inside the current transaction. Any other
           transaction running this same query concurrently will silently
           skip rows already locked by us, instead of blocking on them
           (that's what makes this fast under contention — no worker ever
           queues up waiting behind another worker's claim).
        2. Because the SELECT and the subsequent UPDATE (status -> CLAIMED,
           locked_by_worker_id, locked_until) happen inside one DB
           transaction that we commit atomically, no other worker can
           observe or take these rows in the READY state between the
           SELECT and the UPDATE — they were never released as visible,
           unlocked candidates during that window.
        3. Jobs left behind in RUNNING with an *expired* `locked_until`
           (a worker crashed mid-execution) are included in the same
           candidate set, so they are automatically recovered by whichever
           worker polls next — no separate reaper process, no orphaned work.
        4. `idempotency_key` carries a unique index at the schema level, so
           even a client that double-submits the same logical job cannot
           create two rows to race over in the first place.
        """
        now = datetime.now(timezone.utc)

        # SKIP LOCKED is a Postgres feature; SQLite (used only in fast
        # unit tests) has no row-level locking at all, so we fall back to
        # a plain SELECT there. Production always runs on Postgres, where
        # this is the load-bearing safety mechanism (see docstring above).
        supports_skip_locked = self.db.bind.dialect.name == "postgresql"

        candidates_stmt = (
            select(Job.id)
            .where(
                Job.queue_id == queue_id,
                Job.status.in_([JobStatus.QUEUED, JobStatus.SCHEDULED, JobStatus.RETRYING]),
                (Job.run_at.is_(None)) | (Job.run_at <= now),
            )
            .order_by(Job.priority.desc(), Job.created_at.asc())
            .limit(max_jobs)
        )
        # Include abandoned RUNNING jobs whose visibility timeout expired.
        reclaim_stmt = (
            select(Job.id)
            .where(
                Job.queue_id == queue_id,
                Job.status.in_([JobStatus.CLAIMED, JobStatus.RUNNING]),
                Job.locked_until.is_not(None),
                Job.locked_until < now,
            )
            .order_by(Job.priority.desc(), Job.created_at.asc())
            .limit(max_jobs)
        )
        if supports_skip_locked:
            candidates_stmt = candidates_stmt.with_for_update(skip_locked=True)
            reclaim_stmt = reclaim_stmt.with_for_update(skip_locked=True)

        ready_ids = list(self.db.execute(candidates_stmt).scalars().all())
        remaining = max_jobs - len(ready_ids)
        if remaining > 0:
            ready_ids += list(self.db.execute(reclaim_stmt).scalars().all())[:remaining]

        if not ready_ids:
            return []

        locked_until = now + timedelta(seconds=visibility_timeout_seconds)
        for job_id in ready_ids:
            job = self.db.get(Job, job_id)
            job.status = JobStatus.CLAIMED
            job.locked_by_worker_id = worker_id
            job.locked_until = locked_until

        self.db.flush()
        return [self.db.get(Job, jid) for jid in ready_ids]

    def find_due_scheduled(self, now: datetime) -> list[Job]:
        stmt = select(Job).where(Job.status == JobStatus.SCHEDULED, Job.run_at <= now)
        return list(self.db.execute(stmt).scalars().all())
