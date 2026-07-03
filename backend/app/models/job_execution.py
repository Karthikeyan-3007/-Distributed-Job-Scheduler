import uuid

from sqlalchemy import DateTime, Enum, ForeignKey, Index, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, TimestampMixin, UUIDPrimaryKeyMixin
from app.models.enums import ExecutionStatus


class JobExecution(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """One row per *attempt* of a job. A job with 3 retries has up to 4 rows."""

    __tablename__ = "job_executions"
    __table_args__ = (Index("ix_job_executions_job_attempt", "job_id", "attempt_number", unique=True),)

    job_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False, index=True
    )
    worker_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("workers.id", ondelete="SET NULL"), nullable=True, index=True
    )
    attempt_number: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[ExecutionStatus] = mapped_column(
        Enum(ExecutionStatus, name="execution_status"), nullable=False, default=ExecutionStatus.RUNNING
    )
    started_at: Mapped["DateTime"] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped["DateTime"] = mapped_column(DateTime(timezone=True), nullable=True)
    duration_ms: Mapped[int] = mapped_column(Integer, nullable=True)
    error_message: Mapped[str] = mapped_column(String(2000), nullable=True)

    job: Mapped["Job"] = relationship(back_populates="executions")
    logs: Mapped[list["JobLog"]] = relationship(back_populates="execution", cascade="all, delete-orphan")
