from core.dedupe import find_near_duplicate
from core.db import SessionLocal
from db.models import Program
from datetime import datetime


def test_find_near_duplicate():
    with SessionLocal() as db:
        p = Program(title="Creative Writing for Kids", source="test", source_url="http://x", description_text="Writing workshop for children.", city="Melbourne", dedupe_hash="h", first_seen_at=datetime.utcnow(), last_seen_at=datetime.utcnow(), created_at=datetime.utcnow(), updated_at=datetime.utcnow())
        db.add(p)
        db.commit()
        near = find_near_duplicate(db, "Kids Creative Writing", "A workshop for kids to write.", "Melbourne", 0.3)
        assert near is not None

