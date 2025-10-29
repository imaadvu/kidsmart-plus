from passlib.hash import bcrypt
from core.db import SessionLocal
from db.models import User
from api.auth import create_access_token


def test_password_hash_and_token():
    pw = "secret123"
    h = bcrypt.hash(pw)
    assert bcrypt.verify(pw, h)
    token = create_access_token({"sub": "user-id", "role": "admin"})
    assert isinstance(token, str)

