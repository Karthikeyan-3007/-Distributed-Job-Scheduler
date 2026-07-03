import uuid

from sqlalchemy import func, select

from app.models.job_execution import JobExecution
from app.models.job_log import JobLog
from app.repositories.base import BaseRepository


class JobExecutionRepository(BaseRepository[JobExecution]):
    model = JobExecution

    def next_attempt_number(self, job_id: uuid.UUID) -> int:
        stmt = select(func.count()).select_from(JobExecution).where(JobExecution.job_id == job_id)
        return self.db.execute(stmt).scalar_one() + 1

    def list_for_job(self, job_id: uuid.UUID) -> list[JobExecution]:
        stmt = select(JobExecution).where(JobExecution.job_id == job_id).order_by(JobExecution.attempt_number)
        return list(self.db.execute(stmt).scalars().all())


class JobLogRepository(BaseRepository[JobLog]):
    model = JobLog

    def list_for_execution(self, execution_id: uuid.UUID) -> list[JobLog]:
        stmt = select(JobLog).where(JobLog.job_execution_id == execution_id).order_by(JobLog.created_at)
        return list(self.db.execute(stmt).scalars().all())
