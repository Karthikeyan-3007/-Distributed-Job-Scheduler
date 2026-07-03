import uuid

from sqlalchemy import Boolean, CheckConstraint, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class Queue(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "queues"
    __table_args__ = (
        UniqueConstraint("project_id", "name", name="uq_queue_project_name"),
        CheckConstraint("priority >= 0 AND priority <= 100", name="ck_queue_priority_range"),
        CheckConstraint("concurrency_limit > 0", name="ck_queue_concurrency_positive"),
        CheckConstraint("max_retries >= 0", name="ck_queue_max_retries_nonneg"),
        CheckConstraint("timeout_seconds > 0", name="ck_queue_timeout_positive"),
        CheckConstraint("visibility_timeout_seconds > 0", name="ck_queue_visibility_positive"),
    )

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True
    )
    # Higher number = higher priority. Indexed because the claim query
    # always orders READY jobs by (queue priority, job priority, created_at).
    priority: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    concurrency_limit: Mapped[int] = mapped_column(Integer, nullable=False, default=5)
    max_retries: Mapped[int] = mapped_column(Integer, nullable=False, default=3)
    timeout_seconds: Mapped[int] = mapped_column(Integer, nullable=False, default=300)
    # If a worker claims a job and does not report completion within this
    # window, the job is considered abandoned and becomes reclaimable.
    visibility_timeout_seconds: Mapped[int] = mapped_column(Integer, nullable=False, default=60)
    is_paused: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    project: Mapped["Project"] = relationship(back_populates="queues")
    jobs: Mapped[list["Job"]] = relationship(back_populates="queue", cascade="all, delete-orphan")
    retry_policy: Mapped["RetryPolicy"] = relationship(
        back_populates="queue", uselist=False, cascade="all, delete-orphan"
    )
