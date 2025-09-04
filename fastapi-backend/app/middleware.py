import time
from typing import Callable

from fastapi import FastAPI, Request
from starlette.responses import Response

from .logger import log_background


def add_request_logging(app: FastAPI) -> None:
    @app.middleware("http")
    async def request_logging_middleware(request: Request, call_next: Callable) -> Response:
        start_time = time.time()
        method = request.method
        path = request.url.path

        await log_background(
            stack="backend",
            level="info",
            pkg="request",
            message=f"{method} {path}",
            meta={
                "client_host": request.client.host if request.client else None,
            },
        )

        try:
            response: Response = await call_next(request)
            status_code = response.status_code
            duration_ms = int((time.time() - start_time) * 1000)

            await log_background(
                stack="backend",
                level="info",
                pkg="response",
                message=f"{method} {path}",
                meta={
                    "status": status_code,
                    "duration_ms": duration_ms,
                },
            )

            return response
        except Exception as exc:
            duration_ms = int((time.time() - start_time) * 1000)
            await log_background(
                stack="backend",
                level="error",
                pkg="middleware",
                message=f"{method} {path} exception",
                meta={
                    "error": str(exc),
                    "duration_ms": duration_ms,
                },
            )
            raise 