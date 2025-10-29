from __future__ import annotations
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from core.settings import settings
from loguru import logger
from sqlalchemy.engine import make_url
from db.models import Base


engine = create_engine(settings.sqlalchemy_url, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Auto-create tables in SQLite dev mode for convenience
try:
    url = make_url(settings.sqlalchemy_url)
    if url.get_backend_name().startswith("sqlite"):
        Base.metadata.create_all(engine)
except Exception as e:
    logger.warning(f"DB auto-init skipped: {e}")
