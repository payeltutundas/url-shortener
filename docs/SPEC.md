# URL Shortener: Feature Spec (single source of truth for all agents)

Project root: the repository root (`url-shortener/`)

## Features
1. Paste a long URL, get a short link.
2. Visiting the short link redirects to the original URL.
3. Optional custom alias (e.g. `/my-offer`) and optional expiry date.
4. Each short link counts its clicks.
5. A simple dashboard lists all links with their clicks.

## Tech stack
- Back end: Python, FastAPI, SQLAlchemy 2.x, psycopg 3 (`psycopg[binary]`), pydantic-settings. Tables are created with `Base.metadata.create_all` (no Alembic, to keep it beginner-friendly).
- Database: PostgreSQL 16 in Docker (`docker-compose.yml`). Two databases: `urlshortener` (app) and `urlshortener_test` (tests only).
- Front end: React (Vite, plain JavaScript, no TypeScript). Dev server on port 5173, proxies `/api` to the back end.
- Tests: pytest + FastAPI TestClient against the **test** database.

## Folder layout
```
backend/app/   main.py, config.py, database.py, models.py, schemas.py, validation.py, routes/links.py, routes/redirect.py
backend/requirements.txt
frontend/      Vite React app (src/App.jsx, ShortenForm.jsx, LinksTable.jsx, api.js, styles.css)
tests/         conftest.py, test_shorten.py, test_redirect.py, test_alias.py, test_expiry.py, test_validation.py
docs/          SPEC.md, verification-report.md, screenshots/
docker-compose.yml, docker/initdb/, .env.example, .gitignore, pytest.ini, README.md
```
A single Python virtual environment lives at `.venv` in the project root (shared by back end and tests).
`pytest.ini` sets `pythonpath = backend` and `testpaths = tests`.

## Configuration (environment variables, read from `.env`, never hard-coded)
`DATABASE_URL`, `TEST_DATABASE_URL`, `BASE_URL` (default `http://localhost:8000`), `FRONTEND_ORIGIN` (default `http://localhost:5173`).
`.env` already exists with real local values and must never be printed, committed or copied into code. `.env.example` has fake values.

## API
| Method & path | What it does | Success | Errors |
|---|---|---|---|
| `POST /api/links` body `{url, alias?, expires_at?}` | Create a short link | 201 `{code, short_url, original_url, expires_at, clicks, created_at}` | 422 invalid URL / alias / past expiry; 409 alias already taken |
| `GET /{code}` | Redirect and add 1 click | 307 to original URL | 404 unknown code; 410 expired |
| `GET /api/links` | All links, newest first, each with `clicks` and `status` (`active` or `expired`) | 200 list | |
| `GET /api/health` | Health check | 200 `{"status":"ok"}` | |

- `short_url` = `BASE_URL + "/" + code`.
- Click count is increased atomically in the database (`UPDATE ... SET clicks = clicks + 1`), never read-then-write.
- Expired links do NOT redirect and do NOT count clicks.

## Rules
- **Short code:** 7 random characters from letters and digits, generated with Python `secrets`; retry on a unique-constraint collision.
- **Alias:** 3 to 32 characters, only `A-Za-z0-9_-`, case-sensitive, unique. Reserved (rejected): `api`, `docs`, `redoc`, `openapi.json`, `health`, `static`, `assets`, `favicon.ico`.
- **Expiry:** optional, must be in the future, stored as UTC (timezone-aware).
- **URL validation:** only `http` and `https`; must have a host; max 2048 characters; reject `javascript:`, `data:`, `file:` and anything else; reject a URL whose host is the app's own short-link host (redirect loop).

## Security basics
- No passwords or keys in code. `.env` is in `.gitignore`.
- Database access only through SQLAlchemy (parameterised), never string-built SQL.
- CORS allows only `FRONTEND_ORIGIN`.
- The database port is bound to `127.0.0.1` only.
- Known limits (state them honestly in the README): no login (the dashboard shows all links) and no rate limiting.

## Dashboard (front end)
Form: URL (required), alias (optional), expiry date-time (optional). Table: short link with a Copy button, original URL, clicks, expiry or status, created time. The table refreshes after a link is created and every 10 seconds. Show clear error messages from the API (for example "That alias is already taken").

## Commands (Windows PowerShell, from the project root)
```
docker compose up -d                                                # start the database
.venv\Scripts\python -m uvicorn app.main:app --app-dir backend --reload   # API on :8000
cd frontend; npm run dev                                            # app on :5173
.venv\Scripts\python -m pytest                                      # tests
```
