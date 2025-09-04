import os
import json
import asyncio
from typing import Any, Dict, Optional

import httpx

LOGGER_BASE_URL = os.getenv("LOGGER_BASE_URL", "http://node-logger:4000")
LOGGER_ENDPOINT = f"{LOGGER_BASE_URL.rstrip('/')}/log"


async def log(stack: str, level: str, pkg: str, message: str, meta: Optional[Dict[str, Any]] = None) -> None:
    payload = {
        "stack": stack,
        "level": level,
        "pkg": pkg,
        "message": message,
        "meta": meta or {},
    }

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            await client.post(LOGGER_ENDPOINT, json=payload)
    except Exception as exc:
        # Non-blocking fallback: print a warning locally if logger service is down
        print(f"[logger warning] Failed to send log to Node logger: {exc}. Payload={json.dumps(payload)}")


async def log_background(*args: Any, **kwargs: Any) -> None:
    try:
        await log(*args, **kwargs)
    except Exception:
        # Swallow errors to avoid impacting application flow
        pass 