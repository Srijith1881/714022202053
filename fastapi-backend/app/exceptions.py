from typing import Any
import traceback

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from .logger import log_background


def add_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        tb = traceback.format_exc()
        await log_background(
            stack="backend",
            level="error",
            pkg="exception",
            message=f"Unhandled exception at {request.method} {request.url.path}",
            meta={
                "error": str(exc),
                "trace": tb,
            },
        )
        return JSONResponse(
            status_code=500,
            content={
                "detail": "Internal Server Error",
            },
        ) 