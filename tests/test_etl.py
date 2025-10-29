from core.db import SessionLocal
from core.etl import upsert_program
from adapters.base import ProgramRecord


def test_upsert_program_smoke():
    with SessionLocal() as db:
        rec = ProgramRecord(title="Test Program", source="test", source_url="http://example.com")
        action, p = upsert_program(db, rec)
        db.commit()
        assert action in ("inserted", "updated")

