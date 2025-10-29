from adapters.library_vic import VicLibraryAdapter
from core.settings import settings
import types


class DummyResp:
    def __init__(self, text: str):
        self.text = text

    def raise_for_status(self):
        return None


def test_adapter_falls_back_without_playwright(monkeypatch):
    # Force flag on, but ensure import fails so it falls back to requests
    settings.enable_playwright = True
    adapter = VicLibraryAdapter()

    # Monkeypatch requests.get to return predictable HTML for both robots and page
    import adapters.library_vic as mod

    def fake_get(url, headers=None, timeout=10):
        if url.endswith("robots.txt"):
            return DummyResp("User-agent: *\nAllow: /\n")
        return DummyResp("<html><body><article><a href='x'>X</a><div class='summary'>Hi</div></article></body></html>")

    monkeypatch.setattr(mod, "requests", types.SimpleNamespace(get=fake_get))

    # Monkeypatch _fetch_with_playwright to raise ImportError to simulate missing dep
    def boom(url: str):
        raise ImportError("no playwright")

    monkeypatch.setattr(VicLibraryAdapter, "_fetch_with_playwright", staticmethod(boom))

    raw = adapter.fetch_raw("http://example.org/page")
    assert raw["fetch_agent"] == "requests+bs4"
    items = list(adapter.parse(raw))
    assert items and items[0].title

