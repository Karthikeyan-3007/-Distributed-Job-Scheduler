from app.models.enums import RetryStrategy
from app.models.job import Job
from app.models.retry_policy import RetryPolicy
from app.services.retry_engine import RetryEngine


def make_job(retry_count: int, max_retries: int = 3) -> Job:
    return Job(
        name="test-job",
        job_type="immediate",
        queue_id=None,
        retry_count=retry_count,
        max_retries=max_retries,
        payload={},
    )


def test_fixed_delay_is_constant():
    policy = RetryPolicy(strategy=RetryStrategy.FIXED, base_delay_seconds=10, max_delay_seconds=100)
    assert policy.compute_delay_seconds(1) == 10
    assert policy.compute_delay_seconds(5) == 10


def test_linear_backoff_scales_with_attempt():
    policy = RetryPolicy(strategy=RetryStrategy.LINEAR, base_delay_seconds=5, max_delay_seconds=100)
    assert policy.compute_delay_seconds(1) == 5
    assert policy.compute_delay_seconds(3) == 15


def test_exponential_backoff_doubles():
    policy = RetryPolicy(strategy=RetryStrategy.EXPONENTIAL, base_delay_seconds=2, max_delay_seconds=1000)
    assert policy.compute_delay_seconds(1) == 2
    assert policy.compute_delay_seconds(2) == 4
    assert policy.compute_delay_seconds(3) == 8


def test_delay_is_capped_at_max():
    policy = RetryPolicy(strategy=RetryStrategy.EXPONENTIAL, base_delay_seconds=100, max_delay_seconds=150)
    assert policy.compute_delay_seconds(5) == 150


def test_retry_allowed_when_under_limit():
    job = make_job(retry_count=0, max_retries=3)
    policy = RetryPolicy(strategy=RetryStrategy.FIXED, base_delay_seconds=5, max_delay_seconds=60)
    decision = RetryEngine.decide(job, policy)
    assert decision.should_retry is True
    assert decision.next_run_at is not None


def test_retry_exhausted_routes_to_dead_letter():
    job = make_job(retry_count=3, max_retries=3)
    policy = RetryPolicy(strategy=RetryStrategy.FIXED, base_delay_seconds=5, max_delay_seconds=60)
    decision = RetryEngine.decide(job, policy)
    assert decision.should_retry is False
    assert decision.next_run_at is None
