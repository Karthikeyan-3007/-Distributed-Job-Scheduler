from datetime import datetime, timezone

from croniter import croniter
from sqlalchemy.orm import Session

from app.models.enums import JobStatus, JobType
from app.models.job import Job
from app.repositories.worker_repository import ScheduledJobRepository


class SchedulerService:
    """
    Runs on a tick (see app/scheduler/scheduler.py). Its only job is to
    turn due ScheduledJob *templates* into concrete Job rows and advance
    next_run_at using the cron expression. It never executes jobs itself —
    that stays the worker's responsibility — which keeps "deciding what
    should run" cleanly separated from "running it".
    """

    def __init__(self, db: Session):
        self.db = db
        self.scheduled = ScheduledJobRepository(db)

    def materialize_due_jobs(self) -> int:
        now = datetime.now(timezone.utc)
        due = self.scheduled.find_due(now)
        created = 0
        for template in due:
            job = Job(
                queue_id=template.queue_id,
                name=template.name,
                job_type=JobType.RECURRING,
                status=JobStatus.QUEUED,
                payload=template.job_template or {},
                cron_expression=template.cron_expression,
                max_retries=(template.job_template or {}).get("max_retries", 3),
            )
            self.db.add(job)
            template.last_run_at = now
            template.next_run_at = croniter(template.cron_expression, now).get_next(datetime)
            created += 1
        if due:
            self.db.commit()
        return created
