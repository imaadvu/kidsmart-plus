import subprocess
import sys
import os


def main():
    try:
        subprocess.check_call([sys.executable, "-m", "alembic", "upgrade", "head"])
    except Exception as e:
        print(f"Warning: migration failed or skipped: {e}")
    # Seed demo data if empty
    try:
        from core.db import SessionLocal
        from db.models import Program, User
        from datetime import datetime, timedelta
        from core.nlp import compute_dedupe_hash
        from passlib.hash import bcrypt
        from core.settings import settings

        with SessionLocal() as db:
            if db.query(Program).count() == 0:
                now = datetime.utcnow()
                samples = [
                    ("Storytime for Toddlers", "vic_library", "https://example.org/storytime", "Early years storytime at the library.", "Melbourne", now + timedelta(days=7)),
                    ("Creative Writing Workshop", "eventbrite", "https://example.org/writing", "Improve your writing skills.", "Sydney", now + timedelta(days=14)),
                    ("Preschool Reading Club", "meetup", "https://example.org/reading", "Reading fun for preschoolers.", "Brisbane", now + timedelta(days=21)),
                ]
                for title, source, url, desc, city, dt in samples:
                    dh = compute_dedupe_hash(title, dt.isoformat(), city)
                    db.add(Program(title=title, source=source, source_url=url, description_text=desc, city=city, start_datetime=dt, dedupe_hash=dh, first_seen_at=now, last_seen_at=now, created_at=now, updated_at=now))
                db.commit()
                print("Seeded demo data")
            # Ensure admin user exists
            admin = db.query(User).filter(User.username == settings.admin_username).one_or_none()
            if not admin:
                db.add(User(username=settings.admin_username, hashed_password=bcrypt.hash(settings.admin_password), role="admin"))
                db.commit()
                print("Created admin user from env")
    except Exception as e:
        print(f"Seeding skipped: {e}")
    import uvicorn

    uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=False)


if __name__ == "__main__":
    main()
