import uuid

from sqlalchemy import Enum, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, TimestampMixin, UUIDPrimaryKeyMixin
from app.models.enums import LogLevel


class JobLog(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "job_logs"

    job_execution_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("job_executions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    level: Mapped[LogLevel] = mapped_column(Enum(LogLevel, name="log_level"), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)

    execution: Mapped["JobExecution"] = relationship(back_populates="logs")
