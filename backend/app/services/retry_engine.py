from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from app.models.job import Job
from app.models.retry_policy import RetryPolicy


@dataclass
class RetryDecision:
    should_retry: bool
    next_run_at: datetime | None
    delay_seconds: int | None


class RetryEngine:
    """
    Isolated, side-effect-free retry decision logic. Kept separate from the
    worker's execution loop so it can be unit tested exhaustively without
    a database, an event loop, or a running worker process.
    """

    @staticmethod
    def decide(job: Job, retry_policy: RetryPolicy | None) -> RetryDecision:
        attempt_number = job.retry_count + 1
        if attempt_number > job.max_retries:
            return RetryDecision(should_retry=False, next_run_at=None, delay_seconds=None)

        policy = retry_policy or RetryPolicy(strategy="fixed", base_delay_seconds=5, max_delay_seconds=300)
        delay = policy.compute_delay_seconds(attempt_number)
        next_run_at = datetime.now(timezone.utc) + timedelta(seconds=delay)
        return RetryDecision(should_retry=True, next_run_at=next_run_at, delay_seconds=delay)
