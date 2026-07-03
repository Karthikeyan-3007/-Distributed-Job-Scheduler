"""
Standalone scheduler process.

Run with:  python -m app.scheduler.scheduler

Responsibilities (deliberately narrow, per single-responsibility):
  1. Tick loop that materializes due ScheduledJob (cron) templates into
     concrete Job rows.
  2. Tick loop that marks workers CRASHED once their heartbeat goes stale,
     so the dashboard reflects reality quickly (actual job recovery still
     happens lazily/correctly via the visibility timeout in claim_jobs,
     independent of this process — the scheduler is an observability
     nicety here, not a correctness dependency).
"""

import time

from app.config.settings import get_settings
from app.database.session import SessionLocal
from app.services.scheduler_service import SchedulerService
from app.services.worker_service import WorkerService
from app.utils.logger import configure_logging, get_logger

configure_logging()
logger = get_logger("scheduler")
settings = get_settings()


def tick() -> None:
    db = SessionLocal()
    try:
        created = SchedulerService(db).materialize_due_jobs()
        if created:
            logger.info(f"Materialized {created} recurring job instance(s)")

        stale = WorkerService(db).mark_stale_as_crashed(settings.WORKER_HEARTBEAT_TIMEOUT_SECONDS)
        if stale:
            logger.warning(f"Marked {len(stale)} worker(s) as crashed (heartbeat timeout)")
    finally:
        db.close()


def run() -> None:
    logger.info("Scheduler loop starting")
    while True:
        try:
            tick()
        except Exception as exc:  # noqa: BLE001
            logger.error(f"Scheduler tick failed: {exc}", exc_info=True)
        time.sleep(settings.SCHEDULER_TICK_SECONDS)


if __name__ == "__main__":
    run()
