Architecture Overview

- Backend: FastAPI (Python 3.11), SQLAlchemy 2.0, Alembic, Pydantic v2
- ETL: Modular SourceAdapter pipeline (discover → fetch_raw → parse → normalize → dedupe → upsert)
- NLP: Keyword rules + optional TF-IDF for tagging and explainability
- DB: PostgreSQL with tables: programs, organizations, locations, tags, sources, runs, snapshots, audit_log
- Tasks: Celery + Redis for scheduled ETL
- UI: Streamlit dashboard (talks to API only)

Data Flow
1) Adapters read robots.txt/TOS (record provenance)
2) discover() yields canonical IDs/URLs
3) fetch_raw() retrieves HTML/JSON via requests (+cache, retries)
4) parse() yields ProgramRecord
5) Normalize, dedupe by hash and near-dup similarity
6) Upsert into DB; store snapshots and audit
7) API serves filtered views to dashboard

Security & Privacy
- .env secrets, JWT, RBAC (admin/user), rate limiting, input validation
- Provenance ledger including robots status and crawl delay
- Basic CSP headers and HTML escaping

Performance
- HTTP caching (requests-cache), DB indexes (category, start_datetime, city, dedupe_hash)
- API caching for common filters, pagination, and async queries (optional)

