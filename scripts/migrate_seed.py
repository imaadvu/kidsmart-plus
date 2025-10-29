import sqlite3
from core.db import SessionLocal
from db.models import Program
from core.nlp import compute_dedupe_hash
from datetime import datetime
import pathlib


def migrate_sqlite(sqlite_path: str):
    if not pathlib.Path(sqlite_path).exists():
        print(f"No sqlite file at {sqlite_path}")
        return
    conn = sqlite3.connect(sqlite_path)
    cur = conn.cursor()
    try:
        cur.execute("SELECT title, link, content FROM results")
    except Exception:
        print("Table 'results' not found; skipping")
        return
    rows = cur.fetchall()
    with SessionLocal() as db:
        for title, link, content in rows[:200]:
            dh = compute_dedupe_hash(title or "Untitled", None, None)
            if db.query(Program).filter(Program.dedupe_hash == dh).first():
                continue
            p = Program(
                title=title or "Untitled",
                source="legacy",
                source_url=link or "",
                description_text=content or "",
                dedupe_hash=dh,
                first_seen_at=datetime.utcnow(),
                last_seen_at=datetime.utcnow(),
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )
            db.add(p)
        db.commit()
    print(f"Migrated {len(rows)} rows from sqlite")


if __name__ == "__main__":
    migrate_sqlite("search_results.db")

