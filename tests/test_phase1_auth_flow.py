from fastapi.testclient import TestClient
from api.main import app


client = TestClient(app)


def test_seed_admin_and_login_happy_sad():
    r = client.post("/seed_admin")
    assert r.status_code == 200
    # happy
    r = client.post("/login", json={"username": "admin", "password": "change-me"})
    assert r.status_code == 200
    token = r.json()["access_token"]
    assert token
    # sad
    r2 = client.post("/login", json={"username": "admin", "password": "wrong"})
    assert r2.status_code == 401


def test_ingest_requires_admin():
    r = client.post("/ingest/run")
    assert r.status_code in (401, 403)

