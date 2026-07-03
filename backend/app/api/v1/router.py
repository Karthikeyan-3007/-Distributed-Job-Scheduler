from fastapi import APIRouter

from app.api.v1 import auth, jobs, metrics, projects, queues, workers

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(projects.router)
api_router.include_router(queues.router)
api_router.include_router(jobs.router)
api_router.include_router(workers.router)
api_router.include_router(metrics.router)
