import uuid
from datetime import datetime, timedelta, timezone

from app.models.enums import JobStatus, JobType
from app.models.job import Job
from app.models.organization import Organization
from app.models.project import Project
from app.models.queue import Queue
from app.models.retry_policy import RetryPolicy
from app.models.user import User
from app.repositories.job_repository import JobRepository


def _seed_queue(db, concurrency_limit=2, visibility_timeout=60):
    user = User(email="a@test.com", hashed_password="x", full_name="A")
    db.add(user)
    db.flush()
    org = Organization(name="org", owner_id=user.id)
    db.add(org)
    db.flush()
    project = Project(organization_id=org.id, name="proj")
    db.add(project)
    db.flush()
    queue = Queue(
        project_id=project.id,
        name="q",
        concurrency_limit=concurrency_limit,
        visibility_timeout_seconds=visibility_timeout,
    )
    db.add(queue)
    db.flush()
    db.add(RetryPolicy(queue_id=queue.id))
    db.commit()
    return queue


def test_claim_jobs_returns_only_ready_jobs(db_session):
    queue = _seed_queue(db_session)
    ready = Job(
        queue_id=queue.id, name="ready", job_type=JobType.IMMEDIATE, status=JobStatus.QUEUED, payload={}
    )
    future = Job(
        queue_id=queue.id,
        name="future",
        job_type=JobType.DELAYED,
        status=JobStatus.SCHEDULED,
        run_at=datetime.now(timezone.utc) + timedelta(hours=1),
        payload={},
    )
    db_session.add_all([ready, future])
    db_session.commit()

    worker_id = uuid.uuid4()
    claimed = JobRepository(db_session).claim_jobs(
        queue.id, worker_id, max_jobs=10, visibility_timeout_seconds=60
    )

    assert [j.id for j in claimed] == [ready.id]
    assert ready.status == JobStatus.CLAIMED
    assert ready.locked_by_worker_id == worker_id


def test_claim_jobs_respects_priority_order(db_session):
    queue = _seed_queue(db_session)
    low = Job(
        queue_id=queue.id,
        name="low",
        job_type=JobType.IMMEDIATE,
        status=JobStatus.QUEUED,
        priority=1,
        payload={},
    )
    high = Job(
        queue_id=queue.id,
        name="high",
        job_type=JobType.IMMEDIATE,
        status=JobStatus.QUEUED,
        priority=9,
        payload={},
    )
    db_session.add_all([low, high])
    db_session.commit()

    claimed = JobRepository(db_session).claim_jobs(
        queue.id, uuid.uuid4(), max_jobs=10, visibility_timeout_seconds=60
    )

    assert claimed[0].id == high.id


def test_claim_jobs_never_returns_duplicates_within_batch(db_session):
    queue = _seed_queue(db_session)
    for i in range(3):
        db_session.add(
            Job(
                queue_id=queue.id,
                name=f"j{i}",
                job_type=JobType.IMMEDIATE,
                status=JobStatus.QUEUED,
                payload={},
            )
        )
    db_session.commit()

    claimed = JobRepository(db_session).claim_jobs(
        queue.id, uuid.uuid4(), max_jobs=10, visibility_timeout_seconds=60
    )
    ids = [j.id for j in claimed]

    assert len(ids) == 3
    assert len(set(ids)) == 3  # no duplicates


def test_claim_jobs_reclaims_abandoned_running_jobs(db_session):
    queue = _seed_queue(db_session)
    abandoned = Job(
        queue_id=queue.id,
        name="abandoned",
        job_type=JobType.IMMEDIATE,
        status=JobStatus.RUNNING,
        locked_until=datetime.now(timezone.utc) - timedelta(seconds=5),
        payload={},
    )
    db_session.add(abandoned)
    db_session.commit()

    claimed = JobRepository(db_session).claim_jobs(
        queue.id, uuid.uuid4(), max_jobs=10, visibility_timeout_seconds=60
    )

    assert [j.id for j in claimed] == [abandoned.id]


def test_second_claim_call_gets_nothing_once_all_jobs_taken(db_session):
    queue = _seed_queue(db_session)
    db_session.add(
        Job(queue_id=queue.id, name="only", job_type=JobType.IMMEDIATE, status=JobStatus.QUEUED, payload={})
    )
    db_session.commit()

    repo = JobRepository(db_session)
    first = repo.claim_jobs(queue.id, uuid.uuid4(), max_jobs=10, visibility_timeout_seconds=60)
    second = repo.claim_jobs(queue.id, uuid.uuid4(), max_jobs=10, visibility_timeout_seconds=60)

    assert len(first) == 1
    assert len(second) == 0
