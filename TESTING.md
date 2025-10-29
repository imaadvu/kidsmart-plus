Testing Strategy

Layers
- Unit tests: parsing functions for adapters using fixtures (offline JSON/HTML)
- Integration: ETL on curated sample data; assert upsert & dedupe
- API smoke: /health, /programs filters, /stats
- UI sanity: Streamlit page renders and filter roundtrip (mock API)

Guidelines
- Mock network calls; deterministic seeds
- Keep tests fast; use SQLite for local integration
- Use pytest, httpx, and testcontainers optional for Postgres

Commands
- `make test` – run all tests

