from __future__ import annotations
from typing import Iterable
from loguru import logger
from sqlalchemy.orm import Session
from adapters.base import SourceAdapter, ProgramRecord
from adapters.eventbrite import EventbriteAdapter
from adapters.library_vic import VicLibraryAdapter
from adapters.meetup import MeetupAdapter
from core.nlp import compute_dedupe_hash
from db.models import Program, Snapshot, Run
from datetime import datetime
import hashlib
from core.dedupe import find_near_duplicate, near_duplicate_indices
from core.settings import settings
from core.geo import geocode_address_cached


ADAPTERS: list[SourceAdapter] = [EventbriteAdapter(), MeetupAdapter(), VicLibraryAdapter()]

try:
    from celery import Celery
    from core.settings import settings
    from celery.schedules import crontab

    celery_app = Celery(
        "kidssmart",
        broker=settings.redis_url,
        backend=settings.redis_url,
    )
    celery_app.conf.beat_schedule = {
        "nightly-ingest": {
            "task": "core.etl.run_ingest_task",
            "schedule": crontab(hour=3, minute=0),  # 03:00 daily
        }
    }

    @celery_app.task
    def run_ingest_task():
        from core.db import SessionLocal

        with SessionLocal() as db:
            ingest_all_sources(db)
        return {"status": "ok"}

except Exception:
    celery_app = None  # Optional in bare environments


def upsert_program(db: Session, rec: ProgramRecord) -> tuple[str, Program]:
    date_key = rec.dedupe_key_date or (rec.start_datetime.isoformat() if rec.start_datetime else "")
    dhash = compute_dedupe_hash(rec.title, date_key, rec.city)
    existing = db.query(Program).filter(Program.dedupe_hash == dhash).one_or_none()
    if existing:
        existing.last_seen_at = datetime.utcnow()
        existing.updated_at = datetime.utcnow()
        # If content changed, update description and snapshot
        changed = False
        if rec.description_text and rec.description_text != (existing.description_text or ""):
            existing.description_text = rec.description_text
            existing.status = "updated"
            changed = True
        if rec.category and rec.category != existing.category:
            existing.category = rec.category
            changed = True
        if rec.tags:
            existing.tags = list(sorted(set((existing.tags or []) + rec.tags)))
            changed = True
        if changed and rec.snapshot_excerpt:
            snap = Snapshot(program_id=existing.id, excerpt=rec.snapshot_excerpt, checksum=hashlib.sha256(rec.snapshot_excerpt.encode()).hexdigest())
            db.add(snap)
        return "updated", existing
    # Near-duplicate detection
    near = find_near_duplicate(db, rec.title, rec.description_text, rec.city, settings.neardup_threshold)
    if near is not None:
        # Treat as update to near-duplicate
        near.last_seen_at = datetime.utcnow()
        near.updated_at = datetime.utcnow()
        if rec.description_text and rec.description_text != (near.description_text or ""):
            near.description_text = rec.description_text
            near.status = "updated"
            if rec.snapshot_excerpt:
                snap = Snapshot(program_id=near.id, excerpt=rec.snapshot_excerpt, checksum=hashlib.sha256(rec.snapshot_excerpt.encode()).hexdigest())
                db.add(snap)
        return "updated", near

    p = Program(
        title=rec.title,
        organizer=rec.organizer,
        source=rec.source,
        source_url=rec.source_url,
        category=rec.category,
        subcategory=rec.subcategory,
        start_datetime=rec.start_datetime,
        end_datetime=rec.end_datetime,
        timezone=rec.timezone,
        venue_name=rec.venue_name,
        address=rec.address,
        city=rec.city,
        state=rec.state,
        country=rec.country,
        lat=rec.lat,
        lon=rec.lon,
        online_flag=bool(rec.online_flag),
        audience_age_min=rec.audience_age_min,
        audience_age_max=rec.audience_age_max,
        price_amount=rec.price_amount,
        price_currency=rec.price_currency,
        free_flag=bool(rec.free_flag) if rec.free_flag is not None else None,
        description_text=rec.description_text,
        tags=rec.tags,
        languages=rec.languages,
        provenance=rec.provenance,
        reason_tags=rec.reason_tags,
        dedupe_hash=dhash,
    )
    db.add(p)
    db.flush()
    # Geocode if missing coords and have address-like info
    if p.lat is None and p.lon is None and (p.address or p.city):
        coords = geocode_address_cached(
            ", ".join([x for x in [p.address, p.city, p.state, p.country] if x])
        )
        if coords:
            p.lat, p.lon = coords
            db.add(p)
    if rec.snapshot_excerpt:
        snap = Snapshot(program_id=p.id, excerpt=rec.snapshot_excerpt, checksum=hashlib.sha256(rec.snapshot_excerpt.encode()).hexdigest())
        db.add(snap)
    return "inserted", p


def run_adapter(db: Session, adapter: SourceAdapter) -> Run:
    run = Run(source=adapter.name, status="running", inserted=0, updated=0, errors=0, error_samples=[])
    db.add(run)
    db.flush()
    try:
        for ident in adapter.discover():
            try:
                raw = adapter.fetch_raw(ident)
                batch: list[ProgramRecord] = list(adapter.parse(raw))
                # Within-batch near-duplicate suppression
                texts = [
                    "\n".join(
                        filter(
                            None,
                            [
                                r.title,
                                r.city or "",
                                r.dedupe_key_date or "",
                                (r.description_text or "")[:512],
                            ],
                        )
                    )
                    for r in batch
                ]
                sup = near_duplicate_indices(texts, threshold=settings.neardup_threshold)
                if sup:
                    logger.info(f"{adapter.name}:{ident} near-duplicate suppressed: {len(sup)}")
                for idx, rec in enumerate(batch):
                    if idx in sup:
                        continue
                    action, _ = upsert_program(db, rec)
                    if action == "inserted":
                        run.inserted += 1
                    else:
                        run.updated += 1
                db.commit()
            except Exception as e:
                db.rollback()
                logger.exception(f"Error processing {adapter.name}:{ident}")
                run.errors += 1
                if len(run.error_samples or []) < 5:
                    run.error_samples = (run.error_samples or []) + [str(e)]
        run.status = "finished"
        run.finished_at = datetime.utcnow()
        db.commit()
    except Exception:
        db.rollback()
        run.status = "failed"
        run.finished_at = datetime.utcnow()
        db.commit()
    return run


def ingest_all_sources(db: Session) -> list[Run]:
    runs = []
    for adapter in ADAPTERS:
        runs.append(run_adapter(db, adapter))
    return runs
