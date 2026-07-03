import uuid
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.enums import ExecutionStatus, JobStatus, LogLevel
from app.models.job import Job
from app.models.job_execution import JobExecution
from app.models.job_log import JobLog
from app.models.scheduled_job import DeadLetterQueue
from app.repositories.job_execution_repository import JobExecutionRepository, JobLogRepository
from app.repositories.queue_repository import QueueRepository, RetryPolicyRepository
from app.repositories.worker_repository import DeadLetterRepository
from app.services.retry_engine import RetryEngine


class ExecutionService:
    """
    Used by the worker process to move a job through Running -> terminal
    state, recording a full execution history row per attempt and applying
    the retry policy on failure. This is where JobStatus transitions and
    JobExecution bookkeeping live, kept out of the worker's poll loop so
    the loop itself stays a thin orchestrator.
    """

    def __init__(self, db: Session):
        self.db = db
        self.executions = JobExecutionRepository(db)
        self.logs = JobLogRepository(db)
        self.queues = QueueRepository(db)
        self.retry_policies = RetryPolicyRepository(db)
        self.dlq = DeadLetterRepository(db)

    def start_execution(self, job: Job, worker_id: uuid.UUID) -> JobExecution:
        job.status = JobStatus.RUNNING
        execution = JobExecution(
            job_id=job.id,
            worker_id=worker_id,
            attempt_number=self.executions.next_attempt_number(job.id),
            status=ExecutionStatus.RUNNING,
            started_at=datetime.now(timezone.utc),
        )
        self.executions.add(execution)
        self.db.commit()
        return execution

    def log(self, execution: JobExecution, level: LogLevel, message: str) -> None:
        self.logs.add(JobLog(job_execution_id=execution.id, level=level, message=message))
        self.db.commit()

    def complete_success(self, job: Job, execution: JobExecution, duration_ms: int) -> None:
        execution.status = ExecutionStatus.SUCCEEDED
        execution.completed_at = datetime.now(timezone.utc)
        execution.duration_ms = duration_ms
        job.status = JobStatus.COMPLETED
        job.locked_by_worker_id = None
        job.locked_until = None
        self.db.commit()

    def complete_failure(
        self, job: Job, execution: JobExecution, duration_ms: int, error_message: str
    ) -> None:
        execution.status = ExecutionStatus.FAILED
        execution.completed_at = datetime.now(timezone.utc)
        execution.duration_ms = duration_ms
        execution.error_message = error_message[:2000]

        queue = self.queues.get(job.queue_id)
        policy = queue.retry_policy if queue else None

        decision = RetryEngine.decide(job, policy)
        job.retry_count += 1
        job.locked_by_worker_id = None
        job.locked_until = None

        if decision.should_retry:
            job.status = JobStatus.RETRYING
            job.run_at = decision.next_run_at
        else:
            job.status = JobStatus.DEAD_LETTER
            self.dlq.add(
                DeadLetterQueue(
                    job_id=job.id,
                    queue_id=job.queue_id,
                    reason=error_message[:2000],
                    payload_snapshot=job.payload,
                )
            )
        self.db.commit()
