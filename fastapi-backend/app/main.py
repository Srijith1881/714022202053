import os
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse, RedirectResponse
from pydantic import BaseModel
from .middleware import add_request_logging
from .exceptions import add_exception_handlers
from .url_shortener import store, is_valid_url
from .logger import log_background

# Create FastAPI app
app = FastAPI(title="AffordMed FastAPI Backend", version="1.0.0")

# Attach middleware and exception handlers
add_request_logging(app)
add_exception_handlers(app)


class ShortenRequest(BaseModel):
    url: str


@app.get("/health")
async def health() -> JSONResponse:
    return JSONResponse({"status": "ok"})


@app.get("/demo")
async def demo() -> JSONResponse:
    return JSONResponse({"message": "Demo OK"})


@app.post("/shorten")
async def shorten(body: ShortenRequest) -> JSONResponse:
    if not is_valid_url(body.url):
        raise HTTPException(status_code=400, detail="Invalid URL. Use http(s)://...")
    code = store.get_or_create_code(body.url)

    base_url = os.getenv("BASE_URL", "http://localhost:8000").rstrip("/")
    short_path = f"/s/{code}"
    short_url = f"{base_url}{short_path}"

    await log_background(
        stack="backend",
        level="info",
        pkg="shortener",
        message="created short url",
        meta={"code": code, "url": body.url, "short_url": short_url},
    )

    # Return only the final shortened URL
    return JSONResponse({"short_url": short_url})


@app.get("/s/{code}")
async def resolve(code: str):
    url = store.get_url(code)
    if not url:
        raise HTTPException(status_code=404, detail="Not found")

    await log_background(
        stack="backend",
        level="info",
        pkg="shortener",
        message="redirect",
        meta={"code": code, "url": url},
    )

    return RedirectResponse(url)


# Optional: root route
@app.get("/")
async def root() -> JSONResponse:
    return JSONResponse({"service": "fastapi-backend", "version": "1.0.0"}) 