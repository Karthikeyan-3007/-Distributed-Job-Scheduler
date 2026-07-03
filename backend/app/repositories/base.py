import uuid
from typing import Generic, TypeVar

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.database.base import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """
    Encapsulates all raw SQLAlchemy query construction for one model.
    Services depend on this abstraction, not on the ORM directly, so the
    persistence layer can be swapped/mocked without touching business logic
    (Dependency Inversion).
    """

    model: type[ModelType]

    def __init__(self, db: Session):
        self.db = db

    def get(self, id_: uuid.UUID) -> ModelType | None:
        return self.db.get(self.model, id_)

    def list(self, offset: int = 0, limit: int = 20, **filters) -> tuple[list[ModelType], int]:
        stmt = select(self.model)
        count_stmt = select(func.count()).select_from(self.model)
        for key, value in filters.items():
            if value is not None:
                stmt = stmt.where(getattr(self.model, key) == value)
                count_stmt = count_stmt.where(getattr(self.model, key) == value)
        total = self.db.execute(count_stmt).scalar_one()
        rows = self.db.execute(stmt.offset(offset).limit(limit)).scalars().all()
        return list(rows), total

    def add(self, instance: ModelType) -> ModelType:
        self.db.add(instance)
        self.db.flush()
        return instance

    def delete(self, instance: ModelType) -> None:
        self.db.delete(instance)
        self.db.flush()
