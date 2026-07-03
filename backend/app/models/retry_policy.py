import uuid

from sqlalchemy import CheckConstraint, Enum, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, TimestampMixin, UUIDPrimaryKeyMixin
from app.models.enums import RetryStrategy


class RetryPolicy(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "retry_policies"
    __table_args__ = (
        UniqueConstraint("queue_id", name="uq_retry_policy_queue"),
        CheckConstraint("base_delay_seconds > 0", name="ck_retry_base_delay_positive"),
        CheckConstraint("max_delay_seconds >= base_delay_seconds", name="ck_retry_max_ge_base"),
    )

    queue_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("queues.id", ondelete="CASCADE"), nullable=False, index=True
    )
    strategy: Mapped[RetryStrategy] = mapped_column(
        Enum(RetryStrategy, name="retry_strategy"), nullable=False, default=RetryStrategy.EXPONENTIAL
    )
    base_delay_seconds: Mapped[int] = mapped_column(Integer, nullable=False, default=5)
    max_delay_seconds: Mapped[int] = mapped_column(Integer, nullable=False, default=300)

    queue: Mapped["Queue"] = relationship(back_populates="retry_policy")

    def compute_delay_seconds(self, attempt_number: int) -> int:
        """
        attempt_number is 1-indexed (this is the Nth retry).
        Pure function so it is trivially unit-testable in isolation.
        """
        if self.strategy == RetryStrategy.FIXED:
            delay = self.base_delay_seconds
        elif self.strategy == RetryStrategy.LINEAR:
            delay = self.base_delay_seconds * attempt_number
        else:  # EXPONENTIAL
            delay = self.base_delay_seconds * (2 ** (attempt_number - 1))
        return min(delay, self.max_delay_seconds)
