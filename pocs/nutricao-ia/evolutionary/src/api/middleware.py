import time

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


class ResponseTimeMiddleware(BaseHTTPMiddleware):
    """
    Registra o tempo de resposta no header X-Response-Time-Ms.
    Consumido pelas fitness functions de performance para validação em CI.
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        start = time.perf_counter()
        response = await call_next(request)
        elapsed_ms = (time.perf_counter() - start) * 1000
        response.headers["X-Response-Time-Ms"] = f"{elapsed_ms:.2f}"
        return response