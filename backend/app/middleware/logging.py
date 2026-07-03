import time
import uuid

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from app.utils.logger import get_logger

logger = get_logger("access")


class RequestContextMiddleware(BaseHTTPMiddleware):
    """Stamps every request with a request_id (propagated in the response
    header for client-side correlation) and logs latency + status as
    structured JSON — the backbone of request-level observability."""

    async def dispatch(self, request: Request, call_next):
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        start = time.perf_counter()

        response = await call_next(request)

        duration_ms = round((time.perf_counter() - start) * 1000, 2)
        response.headers["X-Request-ID"] = request_id
        logger.info(
            f"{request.method} {request.url.path} -> {response.status_code} ({duration_ms}ms)",
            extra={"request_id": request_id},
        )
        return response
