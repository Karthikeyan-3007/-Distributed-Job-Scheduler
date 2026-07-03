import uuid

from sqlalchemy import JSON, Boolean, DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class ScheduledJob(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """
    Recurring (cron) job definitions. A ScheduledJob is a *template*: the
    scheduler tick reads due templates and materializes a fresh row in
    `jobs` for each firing, keeping the execution history model uniform
    (every unit of work, recurring or not, is a Job + JobExecutions).
    """

    __tablename__ = "scheduled_jobs"
    __table_args__ = (UniqueConstraint("queue_id", "name", name="uq_scheduled_job_queue_name"),)

    queue_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("queues.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    cron_expression: Mapped[str] = mapped_column(String(120), nullable=False)
    job_template: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    next_run_at: Mapped["DateTime"] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    last_run_at: Mapped["DateTime"] = mapped_column(DateTime(timezone=True), nullable=True)


class DeadLetterQueue(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """
    Terminal home for jobs that exhausted max_retries. Kept as its own
    table (rather than just a Job status) so DLQ inspection/replay queries
    never have to scan the much larger, high-churn `jobs` table, and so a
    full payload snapshot can be preserved even if the original job is
    later purged.
    """

    __tablename__ = "dead_letter_queue"

    job_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False, index=True
    )
    queue_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("queues.id", ondelete="CASCADE"), nullable=False, index=True
    )
    reason: Mapped[str] = mapped_column(String(2000), nullable=False)
    payload_snapshot: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    replayed: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
