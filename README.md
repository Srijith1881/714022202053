# AffordMed FastAPI + Node Logger

A production-ready demo that wires a FastAPI backend (Python) to a Node.js logging service (TypeScript wrapper around AffordMed Logger). All FastAPI logs (requests, responses, errors, and custom logs) are forwarded to the Node service, which then forwards to AffordMed (with console fallback in this repo).

## Project Structure

```
project-root/
│── docker-compose.yml
│── .env.example
│── .gitignore
│── README.md
│
├── fastapi-backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── logger.py
│   │   ├── middleware.py
│   │   ├── exceptions.py
│   │   ├── url_shortener.py
│   ├── requirements.txt
│   └── Dockerfile
│
└── node-logger/
    ├── src/
    │   ├── server.ts
    │   └── logger.ts
    ├── package.json
    ├── tsconfig.json
    └── Dockerfile
```

## Environment Variables

Create a `.env` at the repo root for Docker, or set vars in your shell for local runs.

Required for Node logger (dummy ok for demo):
- EMAIL
- NAME
- ROLLNO
- ACCESS_CODE
- CLIENT_ID
- CLIENT_SECRET
- LOGGER_PORT (default: 4000)

Required/optional for FastAPI:
- FASTAPI_PORT (default: 8000)
- LOGGER_BASE_URL (default: http://node-logger:4000 in Docker; http://localhost:4000 for local)
- BASE_URL (used in shortened links; default: http://localhost:8000)
- URL_STORE_PATH (JSON persistence path; default: ./data/url_store.json)

See `.env.example` for the full list.

## Run Locally (no Docker)

Use two terminals.

Terminal A — Node logger:
```
cd node-logger
npm install
# Optional: create node-logger/.env with creds, or set in shell
npx ts-node src/server.ts
```
- Health: http://localhost:4000/health

Terminal B — FastAPI backend:
```
cd fastapi-backend
py -3.10 -m venv .venv
./.venv/Scripts/Activate.ps1   # PowerShell on Windows
pip install -r requirements.txt
$env:LOGGER_BASE_URL = "http://localhost:4000"
$env:BASE_URL = "http://localhost:8000"
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
- Health: http://localhost:8000/health

## Run with Docker

```
# Create .env (copy from .env.example), then:
docker compose up --build
```
- FastAPI: http://localhost:8000
- Node logger: http://localhost:4000

## Endpoints (FastAPI)

- GET `/health`: health check
- GET `/demo`: example route
- POST `/shorten`: create short URL
  - Request: `{ "url": "https://example.com" }`
  - Response: `{ "short_url": "http://<BASE_URL>/s/<code>" }`
- GET `/s/{code}`: redirect to original URL

## Logging Flow

- `middleware.py` logs each request/response.
- `exceptions.py` catches unhandled exceptions and logs with stack trace.
- `logger.py` forwards logs to `POST /log` of the Node service (non-blocking; prints a warning if unreachable).
- Node `server.ts` validates and forwards to AffordMed via `logger.ts` (falls back to console if `affordmed-logger` is unavailable).

## URL Shortener

- In-memory plus JSON persistence at `URL_STORE_PATH` (default `fastapi-backend/data/url_store.json`).
- Idempotent creation: same URL returns same code.
- Codes reset only if you delete the JSON or change the storage path.

## Configuration Tips

- Set `BASE_URL` to your public domain in production so `short_url` is globally usable, e.g. `https://yourdomain.com`.
- For Docker: add `BASE_URL` to root `.env` and ensure it’s passed to the FastAPI service.

## Troubleshooting

- Node package install fails for `affordmed-logger`: The code will fallback to console logging; we intentionally removed the dependency for portability.
- Windows + Docker Desktop: ensure Linux engine and WSL2 backend are enabled.
- OneDrive path issues: move project to a non-OneDrive folder if file locking occurs.

## License

MIT (for interview/demo purposes) 