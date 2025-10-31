KidsSmart+ — Educational Program Intelligence Platform

KidsSmart+ discovers, collects, cleans, categorizes, and analyzes public educational programs (gov/library/event sites). It provides a FastAPI backend, ETL pipeline with modular adapters, a Streamlit dashboard, and ops tooling.

📋 **Quick Reference:** See `QUICK_REFERENCE.txt` or `CURRENT_STATUS.md` for Docker setup help.

Quick Start (Docker)
- Copy `.env.example` to `.env` and fill secrets.
- Run: `docker compose up --build`
- API: `http://localhost:8000` (OpenAPI docs at `/docs`)
- Dashboard (Streamlit): `http://localhost:8501`

**Troubleshooting:**
- **Build timeout?** See `DOCKER_BUILD_FIXES.md`
- **Image conflict?** See `DOCKER_IMAGE_CONFLICT_FIX.md` or run `.\rebuild.ps1`

One-liner: `docker compose --profile prod up -d` (seeds DB and runs first ETL).

Services
- FastAPI (`api`) with JWT auth, rate limiting, caching
- Postgres (`db`) with Alembic migrations
- Redis (`redis`) for Celery tasks and caching
- Celery worker (`worker`) running ETL
- Celery beat (`beat`) scheduling nightly ingest at 03:00 (crontab)
- Streamlit dashboard (`dashboard`) consuming the API

Auth & Admin
- Default admin created from env on first run: `ADMIN_USERNAME`, `ADMIN_PASSWORD`.
- Login: `POST /auth/login` with JSON `{"username","password"}` → JWT bearer token.
- RBAC: admin can call `POST /ingest/run`.

Dev
- `make dev` – Run API + dashboard locally (requires Python 3.11)
- `make etl` – Run ingest for adapters
- `make test` – Run unit/integration tests
- `make seed` – Load demo data

See `ARCHITECTURE.md`, `PRIVACY_COMPLIANCE.md`, and `TESTING.md` for details.

Geocoding & Map
- Toggle geocoding via `GEOCODING_ENABLED=true` in `.env` (uses Nominatim); when enabled, ETL geocodes new addresses and map pins appear on the dashboard.
- Exports available on the dashboard (CSV/JSON) from the current filter set.

Playwright Fallback (JS-rendered pages)
- Enable with `ENABLE_PLAYWRIGHT=true` in `.env`.
- Install dependencies: `pip install playwright` then `python -m playwright install chromium`.
- The Vic Library adapter switches to Playwright when enabled; otherwise uses requests+BS4.
