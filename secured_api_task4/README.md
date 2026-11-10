# Task 4 — Secured API with Integration Tests

## Setup (Windows PowerShell)

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

Edit `.env` and set your own API_KEY and WEBHOOK_SECRET.

## Run API

```powershell
uvicorn src.main:app --reload
```

Open http://127.0.0.1:8000/docs.

Every `/customers` endpoint requires `X-API-Key`. Missing key returns 401; wrong key returns 403. Duplicate email returns 409; invalid request data returns 422.

## Run integration tests

```powershell
pytest -v
pytest --cov=src --cov-report=term-missing
```

The test fixture creates an isolated in-memory SQLite database and overrides the application's database dependency.

## Webhook signature

Sign the exact raw request bytes using HMAC-SHA256 and the `WEBHOOK_SECRET` value. Send the lowercase hexadecimal digest in `X-Signature`. Valid requests are acknowledged with 200 and queued as a FastAPI background task; invalid signatures return 401.

## Pagination client

`src/client.py` exposes `fetch_all(url, ...)`. It uses the mock `/oauth/token` client-credentials endpoint, refreshes on 401, fetches `page`/`per_page` until an empty page, and sleeps when `X-RateLimit-Remaining: 0`.

Example:

```python
from src.client import fetch_all
items = fetch_all("http://127.0.0.1:8000/customers")
print(len(items))
```

Note: the customer API uses API-key auth as required by the CRUD task; `fetch_all` demonstrates bearer-token refresh against the mock OAuth endpoint. In a production integration, configure the resource API to accept the bearer token as well.
