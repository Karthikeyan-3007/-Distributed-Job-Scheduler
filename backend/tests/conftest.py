import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import app.models  # noqa: F401 ensure all models are registered
from app.database.base import Base


@pytest.fixture()
def db_session():
    # SQLite in-memory keeps unit tests fast and hermetic. Postgres-only
    # features used at the DB layer (FOR UPDATE SKIP LOCKED, JSONB) are
    # exercised separately by the concurrency test against a real
    # Postgres instance (see test_concurrent_claiming.py docstring).
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
