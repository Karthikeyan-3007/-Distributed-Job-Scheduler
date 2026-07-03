"""
Standalone worker process.

Run with:  python -m app.workers.worker

A worker is a long-lived process that shares the same database as the API
(this mirrors how real job-scheduler workers operate: they don't have to
go through the HTTP API to touch job state, since they *are* trusted
infrastructure, not untrusted clients). It:

  1. Registers itself as a Worker row on startup.
  2. On every poll tick, for each non-paused queue with spare concurrency,
     atomically claims a batch of ready jobs (see JobRepository.claim_jobs).
  3. Executes claimed jobs concurrently using a thread pool (jobs here are
     simulated/pluggable handlers — see TASK_REGISTRY below; swapping in
     real handlers, e.g. "send_email", is a one-line registration).
  4. Sends periodic heartbeats so the dashboard and the visibility-timeout
     recovery mechanism both know it's alive.
  5. Handles SIGTERM/SIGINT for graceful shutdown: stops claiming new work
     and waits for in-flight jobs to finish before exiting.
"""

import concurrent.futures
import os
import random
import signal
import socket
import time
import uuid

from sqlalchemy import select

from app.config.settings import get_settings
from app.database.session import SessionLocal
from app.models.enums import LogLevel, WorkerStatus
from app.models.job import Job
from app.models.queue import Queue
from app.models.worker import Worker
from app.repositories.job_repository import JobRepository
from app.services.execution_service import ExecutionService
from app.utils.logger import configure_logging, get_logger

configure_logging()
logger = get_logger("worker")
settings = get_settings()


def simulated_task(job: Job) -> None:
    """
    Placeholder task executor. In a real deployment, TASK_REGISTRY maps
    job.name -> a real handler (send_email, resize_image, ...). Here we
    simulate variable-duration work with an occasional failure so the
    retry engine and DLQ path are exercised end-to-end out of the box.
    """
    time.sleep(random.uniform(0.2, 1.2))
    if random.random() < 0.15:
        raise RuntimeError(f"Simulated failure while executing job '{job.name}'")


TASK_REGISTRY = {
    "default": simulated_task,
}


class JobWorker:
    def __init__(self, concurrency: int = 4):
        self.concurrency = concurrency
        self.worker_id: uuid.UUID | None = None
        self._shutdown = False
        self._pool = concurrent.futures.ThreadPoolExecutor(max_workers=concurrency)
        self._in_flight = 0

    def register(self) -> None:
        db = SessionLocal()
        try:
            # os.getpid() is a poor disambiguator here: under Docker, the
            # worker process is PID 1 inside its own container for every
            # replica, so "worker-{pid}" would collide across all of them.
            # hostname (== container ID when running under Docker/Compose)
            # is what's actually unique per replica.
            worker = Worker(
                name=f"worker-{socket.gethostname()}",
                hostname=socket.gethostname(),
                concurrency=self.concurrency,
                status=WorkerStatus.ACTIVE,
            )
            db.add(worker)
            db.commit()
            db.refresh(worker)
            self.worker_id = worker.id
            logger.info(f"Registered worker {worker.id}", extra={"worker_id": str(worker.id)})
        finally:
            db.close()

    def heartbeat(self) -> None:
        from datetime import datetime, timezone

        db = SessionLocal()
        try:
            worker = db.get(Worker, self.worker_id)
            worker.last_heartbeat_at = datetime.now(timezone.utc)
            worker.status = WorkerStatus.ACTIVE if self._in_flight > 0 else WorkerStatus.IDLE
            db.commit()
        finally:
            db.close()

    def poll_and_claim(self) -> list[uuid.UUID]:
        db = SessionLocal()
        claimed_ids: list[uuid.UUID] = []
        try:
            queues = db.execute(select(Queue).where(Queue.is_paused.is_(False))).scalars().all()
            job_repo = JobRepository(db)
            for queue in queues:
                capacity = queue.concurrency_limit - job_repo.count_running(queue.id)
                if capacity <= 0:
                    continue
                available_slots = min(capacity, self.concurrency - self._in_flight)
                if available_slots <= 0:
                    break
                jobs = job_repo.claim_jobs(
                    queue_id=queue.id,
                    worker_id=self.worker_id,
                    max_jobs=available_slots,
                    visibility_timeout_seconds=queue.visibility_timeout_seconds,
                )
                if jobs:
                    db.commit()
                    claimed_ids.extend(j.id for j in jobs)
                    logger.info(
                        f"Claimed {len(jobs)} job(s) from queue {queue.name}",
                        extra={"worker_id": str(self.worker_id), "queue_id": str(queue.id)},
                    )
        finally:
            db.close()
        return claimed_ids

    def execute_job(self, job_id: uuid.UUID) -> None:
        self._in_flight += 1
        db = SessionLocal()
        try:
            job = db.get(Job, job_id)
            svc = ExecutionService(db)
            execution = svc.start_execution(job, self.worker_id)
            start = time.perf_counter()
            handler = TASK_REGISTRY.get(job.name, TASK_REGISTRY["default"])
            try:
                handler(job)
            except Exception as exc:  # noqa: BLE001 - intentional: any task failure is caught here
                duration_ms = int((time.perf_counter() - start) * 1000)
                svc.log(execution, LogLevel.ERROR, str(exc))
                svc.complete_failure(job, execution, duration_ms, str(exc))
                logger.warning(
                    f"Job {job.id} failed (attempt {execution.attempt_number}): {exc}",
                    extra={"worker_id": str(self.worker_id), "job_id": str(job.id)},
                )
            else:
                duration_ms = int((time.perf_counter() - start) * 1000)
                svc.log(execution, LogLevel.INFO, "Job completed successfully")
                svc.complete_success(job, execution, duration_ms)
                logger.info(
                    f"Job {job.id} completed in {duration_ms}ms",
                    extra={"worker_id": str(self.worker_id), "job_id": str(job.id)},
                )
        finally:
            db.close()
            self._in_flight -= 1

    def run(self) -> None:
        self.register()
        signal.signal(signal.SIGTERM, self._handle_shutdown)
        signal.signal(signal.SIGINT, self._handle_shutdown)

        last_heartbeat = 0.0
        futures: list[concurrent.futures.Future] = []

        logger.info(f"Worker loop starting (concurrency={self.concurrency})")
        while not self._shutdown:
            now = time.time()
            if now - last_heartbeat >= settings.WORKER_HEARTBEAT_INTERVAL_SECONDS:
                self.heartbeat()
                last_heartbeat = now

            futures = [f for f in futures if not f.done()]
            if self._in_flight < self.concurrency:
                for job_id in self.poll_and_claim():
                    futures.append(self._pool.submit(self.execute_job, job_id))

            time.sleep(settings.WORKER_POLL_INTERVAL_SECONDS)

        logger.info("Shutdown signal received, draining in-flight jobs...")
        concurrent.futures.wait(futures)
        self._pool.shutdown(wait=True)
        logger.info("Worker stopped cleanly")

    def _handle_shutdown(self, signum, frame) -> None:
        self._shutdown = True


if __name__ == "__main__":
    concurrency = int(os.environ.get("WORKER_CONCURRENCY", "4"))
    JobWorker(concurrency=concurrency).run()
