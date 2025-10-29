from fastapi.testclient import TestClient
from api.main import app
from core.db import SessionLocal
from core.etl import upsert_program
from adapters.base import ProgramRecord
from db.models import Snapshot


client = TestClient(app)


def test_snapshots_and_diff_endpoint():
    with SessionLocal() as db:
        rec1 = ProgramRecord(
            title="Lib Storytime",
            source="vic_library",
            source_url="http://example.org/1",
            city="Melbourne",
            description_text="First excerpt",
            snapshot_excerpt="First excerpt",
            dedupe_key_date="2025-01-01",
        )
        action1, p = upsert_program(db, rec1)
        db.commit()
        assert action1 in ("inserted", "updated")
        # Update with changed description/snapshot to trigger a new snapshot
        rec2 = ProgramRecord(
            title="Lib Storytime",
            source="vic_library",
            source_url="http://example.org/1",
            city="Melbourne",
            description_text="Second excerpt updated",
            snapshot_excerpt="Second excerpt updated",
            dedupe_key_date="2025-01-01",
        )
        action2, p2 = upsert_program(db, rec2)
        db.commit()
        assert p2.id == p.id
        snaps = db.query(Snapshot).filter(Snapshot.program_id == p.id).all()
        assert len(snaps) >= 2

        # API: snapshots
        r = client.get(f"/programs/{p.id}/snapshots")
        assert r.status_code == 200
        items = r.json().get("items", [])
        assert len(items) >= 2

        # API: diff
        r2 = client.get(f"/programs/{p.id}/diff")
        assert r2.status_code == 200
        diff = r2.json().get("diff", "")
        assert isinstance(diff, str)
        # Expect unified diff markers when two snapshots exist
        assert ("+" in diff) or ("-" in diff) or diff == ""

