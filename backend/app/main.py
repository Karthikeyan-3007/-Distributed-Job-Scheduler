from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.config.settings import get_settings
from app.middleware.error_handler import register_exception_handlers
from app.middleware.logging import RequestContextMiddleware
from app.utils.logger import configure_logging

settings = get_settings()
configure_logging()

app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    description=(
        "A production-inspired distributed job scheduling platform: "
        "durable queues, atomic job claiming, configurable retries, "
        "dead-letter handling, and worker/queue observability."
    ),
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(RequestContextMiddleware)
register_exception_handlers(app)

app.include_router(api_router, prefix=settings.API_V1_PREFIX)


@app.get("/")
def root():
    return {"service": settings.APP_NAME, "docs": "/docs"}
