import uuid

from sqlalchemy import DateTime, Enum, Float, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, TimestampMixin, UUIDPrimaryKeyMixin
from app.models.enums import WorkerStatus


class Worker(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "workers"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    hostname: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[WorkerStatus] = mapped_column(
        Enum(WorkerStatus, name="worker_status"), nullable=False, default=WorkerStatus.ACTIVE, index=True
    )
    concurrency: Mapped[int] = mapped_column(Integer, nullable=False, default=4)
    last_heartbeat_at: Mapped["DateTime"] = mapped_column(DateTime(timezone=True), nullable=True, index=True)

    heartbeats: Mapped[list["WorkerHeartbeat"]] = relationship(
        back_populates="worker", cascade="all, delete-orphan"
    )


class WorkerHeartbeat(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """
    Append-only heartbeat history, kept separate from Worker.last_heartbeat_at.
    Worker.last_heartbeat_at is the hot field read on every claim query;
    this table is the cold audit trail used for worker health charts and
    post-mortems, so it doesn't bloat the row workers update every few seconds.
    """

    __tablename__ = "worker_heartbeats"

    worker_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("workers.id", ondelete="CASCADE"), nullable=False, index=True
    )
    active_job_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    cpu_percent: Mapped[float] = mapped_column(Float, nullable=True)
    memory_mb: Mapped[float] = mapped_column(Float, nullable=True)

    worker: Mapped["Worker"] = relationship(back_populates="heartbeats")
