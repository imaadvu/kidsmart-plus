from fastapi.testclient import TestClient
from api.main import app
from core.geo import geocode_address_cached
from core import geo as geo_module
from core.settings import settings


client = TestClient(app)


def test_geocode_disabled_returns_none(monkeypatch):
    settings.geocoding_enabled = False
    geocode_address_cached.cache_clear()  # type: ignore[attr-defined]
    assert geocode_address_cached("1 Test St, Melbourne") is None


def test_geocode_enabled_mock(monkeypatch):
    class FakeLoc:
        latitude = -37.8136
        longitude = 144.9631

    class FakeNom:
        def __init__(self, user_agent: str):
            pass

        def geocode(self, addr: str, timeout: int = 10):
            return FakeLoc()

    settings.geocoding_enabled = True
    geocode_address_cached.cache_clear()  # type: ignore[attr-defined]
    monkeypatch.setattr(geo_module, "Nominatim", FakeNom)
    out = geocode_address_cached("1 Test St, Melbourne")
    assert out == (-37.8136, 144.9631)


def test_programs_payload_shape():
    r = client.get("/programs", params={"size": 1})
    assert r.status_code == 200
    data = r.json()
    assert set(["total", "page", "size", "items"]).issubset(set(data.keys()))
    if data["items"]:
        item = data["items"][0]
        assert "title" in item and "source_url" in item

