import uuid

from sqlalchemy import JSON, CheckConstraint, DateTime, Enum, ForeignKey, Index, Integer, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, TimestampMixin, UUIDPrimaryKeyMixin
from app.models.enums import JobStatus, JobType


class Job(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "jobs"
    __table_args__ = (
        CheckConstraint("priority >= 0 AND priority <= 100", name="ck_job_priority_range"),
        CheckConstraint("retry_count >= 0", name="ck_job_retry_count_nonneg"),
        # This is THE index that makes atomic claiming fast: workers scan
        # for (status=queued/scheduled, run_at<=now) ordered by priority
        # without a sequential scan, even with 1000+ rows in the table.
        Index(
            "ix_jobs_claim_lookup",
            "queue_id",
            "status",
            "run_at",
            "priority",
        ),
        # Unique index (NULLs are treated as distinct by both Postgres and
        # SQLite, so multiple jobs without an idempotency_key are fine;
        # any two jobs that *do* set one can't collide).
        Index("ix_jobs_idempotency_key", "idempotency_key", unique=True),
    )

    queue_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("queues.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    job_type: Mapped[JobType] = mapped_column(Enum(JobType, name="job_type"), nullable=False)
    status: Mapped[JobStatus] = mapped_column(
        Enum(JobStatus, name="job_status"), nullable=False, default=JobStatus.QUEUED, index=True
    )
    # JSONB on Postgres (indexable, binary-efficient); plain JSON elsewhere
    # (e.g. SQLite in unit tests) so the model stays dialect-portable.
    payload: Mapped[dict] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"), nullable=False, default=dict
    )

    priority: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    # NULL means "run as soon as possible". Set in the future for delayed jobs.
    run_at: Mapped["DateTime"] = mapped_column(DateTime(timezone=True), nullable=True)
    cron_expression: Mapped[str] = mapped_column(String(120), nullable=True)

    max_retries: Mapped[int] = mapped_column(Integer, nullable=False, default=3)
    retry_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # Used to atomically fence out duplicate submissions of the same
    # logical job (e.g. client retried an HTTP POST after a timeout).
    idempotency_key: Mapped[str] = mapped_column(String(255), nullable=True)

    # Ownership fencing: which worker currently holds the lease, and until
    # when. A job is reclaimable once locked_until has passed (visibility
    # timeout), even if the worker crashed without reporting failure.
    locked_by_worker_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("workers.id", ondelete="SET NULL"), nullable=True
    )
    locked_until: Mapped["DateTime"] = mapped_column(DateTime(timezone=True), nullable=True)

    batch_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=True, index=True)

    queue: Mapped["Queue"] = relationship(back_populates="jobs")
    executions: Mapped[list["JobExecution"]] = relationship(
        back_populates="job", cascade="all, delete-orphan", order_by="JobExecution.created_at"
    )
