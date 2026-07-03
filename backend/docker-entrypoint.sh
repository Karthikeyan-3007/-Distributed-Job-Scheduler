#!/bin/sh
set -e

echo "Waiting for database..."
python - <<'PY'
import time
from sqlalchemy import create_engine, text
from app.config.settings import get_settings

settings = get_settings()
for attempt in range(30):
    try:
        engine = create_engine(settings.DATABASE_URL)
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("Database is ready.")
        break
    except Exception as exc:
        print(f"DB not ready yet ({exc}); retrying...")
        time.sleep(2)
else:
    raise SystemExit("Database never became available")
PY

echo "Applying schema (create_all bootstrap; use 'alembic revision --autogenerate' for future changes)..."
python - <<'PY'
from sqlalchemy.exc import ProgrammingError
from app.database.session import engine
from app.models import Base

try:
    Base.metadata.create_all(engine)
    print("Schema ready.")
except ProgrammingError as exc:
    # Another container (e.g. a concurrently-starting worker replica) won
    # the race and created the same tables/enums a moment ago. create_all's
    # "does it exist" check and the actual CREATE aren't atomic, so this can
    # legitimately happen under concurrent cold starts. Non-fatal: the
    # schema exists either way, so we log and continue instead of crashing.
    print(f"Schema already being created by another container, continuing: {exc}")
PY

exec "$@"
