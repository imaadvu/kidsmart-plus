from __future__ import annotations
from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from sqlalchemy.orm import Session
from core.settings import settings
from core.db import get_db
from db.models import Program, Run, Source
from api.deps import get_current_user, require_admin
from core.etl import ingest_all_sources
from datetime import datetime
from api.auth import router as auth_router, create_access_token
from api.ratelimit import RateLimitMiddleware
from difflib import unified_diff
from db.models import Snapshot, AuditLog, User
from passlib.hash import bcrypt
import hashlib, json
from api.cache import cache


class CSPMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        response.headers["Content-Security-Policy"] = "default-src 'self' 'unsafe-inline' data:"
        return response


app = FastAPI(title="KidsSmart+ API", version="1.0.0")
app.add_middleware(CSPMiddleware)
app.add_middleware(RateLimitMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)

@app.get("/health")
def health():
    return {"status": "ok", "time": datetime.utcnow().isoformat()}


@app.get("/programs")
def list_programs(
    q: str | None = None,
    category: str | None = None,
    city: str | None = None,
    date_from: str | None = None,
    date_to: str | None = None,
    price_free: bool | None = None,
    online: bool | None = None,
    page: int = 1,
    size: int = 20,
    db: Session = Depends(get_db),
):
    qry = db.query(Program)
    if q:
        qlike = f"%{q.lower()}%"
        qry = qry.filter((Program.title.ilike(qlike)) | (Program.description_text.ilike(qlike)))
    if category:
        qry = qry.filter(Program.category == category)
    if city:
        qry = qry.filter(Program.city == city)
    if online is not None:
        qry = qry.filter(Program.online_flag == online)
    if price_free is not None:
        qry = qry.filter(Program.free_flag == price_free)
    if date_from:
        qry = qry.filter(Program.start_datetime >= date_from)
    if date_to:
        qry = qry.filter(Program.start_datetime <= date_to)
    # cache key
    sig = {"q": q, "category": category, "city": city, "date_from": date_from, "date_to": date_to, "pf": price_free, "on": online, "p": page, "s": size}
    key = "programs:" + hashlib.sha256(json.dumps(sig, sort_keys=True).encode()).hexdigest()
    cached = cache.get_json(key)
    if cached:
        return cached
    total = qry.count()
    items = qry.order_by(Program.start_datetime.desc().nulls_last()).offset((page - 1) * size).limit(size).all()
    payload = {"total": total, "page": page, "size": size, "items": [serialize_program(p) for p in items]}
    cache.set_json(key, payload, ttl=settings.cache_ttl)
    return payload


@app.get("/programs/{pid}")
def get_program(pid: str, db: Session = Depends(get_db)):
    p = db.get(Program, pid)
    if not p:
        raise HTTPException(404, "Not found")
    return serialize_program(p)


@app.get("/stats")
def stats(db: Session = Depends(get_db)):
    count = db.query(Program).count()
    rows = db.execute("SELECT COALESCE(category,'Uncategorized') as c, COUNT(*) FROM programs GROUP BY c").all()
    by_category = {c: n for c, n in rows}
    return {"count": count, "by_category": by_category}


@app.post("/ingest/run")
def trigger_ingest(user=Depends(require_admin), db: Session = Depends(get_db)):
    db.add(AuditLog(actor=user.get("username", "admin"), action="ingest_run", details={}))
    db.commit()
    runs = ingest_all_sources(db)
    return {"runs": [serialize_run(r) for r in runs]}


@app.get("/runs/{rid}")
def get_run(rid: int, db: Session = Depends(get_db)):
    r = db.get(Run, rid)
    if not r:
        raise HTTPException(404, "Not found")
    return serialize_run(r)


def serialize_program(p: Program):
    return {
        "id": str(p.id),
        "title": p.title,
        "organizer": p.organizer,
        "source": p.source,
        "source_url": p.source_url,
        "category": p.category,
        "start_datetime": p.start_datetime.isoformat() if p.start_datetime else None,
        "end_datetime": p.end_datetime.isoformat() if p.end_datetime else None,
        "city": p.city,
        "online_flag": p.online_flag,
        "free_flag": p.free_flag,
        "description_text": p.description_text,
        "tags": p.tags or [],
        "reason_tags": p.reason_tags or [],
        "lat": p.lat,
        "lon": p.lon,
    }


def serialize_run(r: Run):
    return {
        "id": r.id,
        "source": r.source,
        "status": r.status,
        "inserted": r.inserted,
        "updated": r.updated,
        "errors": r.errors,
        "error_samples": r.error_samples or [],
        "started_at": r.started_at.isoformat() if r.started_at else None,
        "finished_at": r.finished_at.isoformat() if r.finished_at else None,
    }


@app.get("/sources")
def list_sources():
    # Static from adapters for now
    return {"items": [
        {"name": "eventbrite", "type": "api"},
        {"name": "meetup", "type": "api"},
        {"name": "vic_library", "type": "html"},
    ]}


@app.get("/programs/{pid}/snapshots")
def program_snapshots(pid: str, db: Session = Depends(get_db)):
    snaps = db.query(Snapshot).filter(Snapshot.program_id == pid).order_by(Snapshot.created_at.desc()).all()
    return {
        "items": [
            {
                "id": s.id,
                "created_at": s.created_at.isoformat(),
                "checksum": s.checksum,
                "excerpt": s.excerpt,
            }
            for s in snaps
        ]
    }


@app.get("/programs/{pid}/diff")
def program_diff(pid: str, db: Session = Depends(get_db)):
    snaps = db.query(Snapshot).filter(Snapshot.program_id == pid).order_by(Snapshot.created_at.desc()).limit(2).all()
    if len(snaps) < 2:
        p = db.get(Program, pid)
        if not p:
            raise HTTPException(404, "Not found")
        return {"diff": "", "note": "Only one version available"}
    a = (snaps[1].excerpt or "").splitlines()
    b = (snaps[0].excerpt or "").splitlines()
    diff = "\n".join(unified_diff(a, b, fromfile="older", tofile="newer", lineterm=""))
    return {"diff": diff}


@app.post("/login")
def login_alias(payload: dict, db: Session = Depends(get_db)):
    username = (payload or {}).get("username")
    password = (payload or {}).get("password")
    if not username or not password:
        raise HTTPException(400, "username and password required")
    user = db.query(User).filter(User.username == username).one_or_none()
    if not user or not bcrypt.verify(password, user.hashed_password):
        raise HTTPException(401, "Invalid credentials")
    user.last_login_at = datetime.utcnow()
    db.add(user)
    db.add(AuditLog(actor=username, action="login", details={}))
    db.commit()
    token = create_access_token({"sub": str(user.id), "username": user.username, "role": user.role})
    return {"access_token": token, "token_type": "bearer"}


@app.post("/seed_admin")
def seed_admin(db: Session = Depends(get_db)):
    uname = settings.admin_username
    pwd = settings.admin_password
    user = db.query(User).filter(User.username == uname).one_or_none()
    if user:
        return {"status": "exists"}
    hashed = bcrypt.hash(pwd)
    user = User(username=uname, hashed_password=hashed, role="admin")
    db.add(user)
    db.add(AuditLog(actor=uname, action="seed_admin", details={}))
    db.commit()
    return {"status": "created", "username": uname}
