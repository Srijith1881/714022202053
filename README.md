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

## Obtain Credentials from Evaluation Service

If you were provided an access code (e.g., `BUeZuD`), register to obtain `clientID` and `clientSecret`.

Create `register.py` and run:
```python
import requests

url = "http://20.244.56.144/evaluation-service/register"
payload = {
  "accessCode": "BUeZuD",
  "email": "your_email@example.com",
  "name": "Your Name",
  "mobileNo": "9999999999",
  "githubUsername": "your-github"
}

r = requests.post(url, json=payload, timeout=15)
print(r.status_code, r.text)
data = r.json()
print("clientId:", data.get("clientId") or data.get("clientID"))
print("clientSecret:", data.get("clientSecret"))
```
- Paste the returned values into your environment (root `.env` or `node-logger/.env`):
```
ACCESS_CODE=BUeZuD
CLIENT_ID=<from-response>
CLIENT_SECRET=<from-response>
EMAIL=your_email@example.com
NAME=Your Name
ROLLNO=YourRollNo
LOGGER_PORT=4000
FASTAPI_PORT=8000
```

## Run Locally (no Docker)

Use two terminals.

Terminal A — Node logger:
```
cd node-logger
npm install
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

## Test Real Shortening

- Create a short URL:
```
curl -Method POST "http://localhost:8000/shorten" -ContentType "application/json" -Body (@{ url="https://example.com" } | ConvertTo-Json)
```
Response:
```
{ "short_url": "http://localhost:8000/s/<code>" }
```
- Open the `short_url` in a browser; it redirects to the original URL.
- Set `BASE_URL` to a public domain (e.g., `https://yourdomain.com`) when deployed so that `short_url` is globally usable.

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

## Configuration Tips

- Set `BASE_URL` to your public domain in production so `short_url` is globally usable.
- For Docker: add `BASE_URL` to root `.env` and ensure it’s passed to the FastAPI service.

## Troubleshooting

- If registration returns 400 with missing fields, include `email`, `name`, `mobileNo`, `githubUsername`.
- If the AffordMed package isn’t available, Node will use console fallback; the system still works end-to-end.
- On Windows, prefer a non-OneDrive folder if file locking occurs.

## License

MIT (for interview/demo purposes) 