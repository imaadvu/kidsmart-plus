PY=python
PIP=pip

.PHONY: dev api dashboard etl seed test fmt

dev:
	$(PY) -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

api:
	$(PY) -m uvicorn api.main:app --host 0.0.0.0 --port 8000

dashboard:
	streamlit run dashboard/app.py --server.port 8501

etl:
	$(PY) scripts/ingest_all.py

seed:
	$(PY) scripts/migrate_seed.py || true
	$(PY) -c "import pathlib; p=pathlib.Path('db/seed.sql'); print('No seed.sql' if not p.exists() else p.read_text())"

test:
	pytest -q

fmt:
	isort . && black .

