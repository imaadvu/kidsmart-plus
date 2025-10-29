from __future__ import annotations
from .base import SourceAdapter, ProgramRecord
from core.nlp import rule_based_tags, normalize_text
from core.settings import settings
import requests
import requests_cache
from bs4 import BeautifulSoup
from typing import Iterable, Any
from datetime import datetime
import time


requests_cache.install_cache("library_cache", expire_after=3600)


class VicLibraryAdapter(SourceAdapter):
    name = "vic_library"
    base_url = "https://www.slv.vic.gov.au"  # Example: State Library Victoria

    def _robots_ok(self) -> tuple[bool, int | None]:
        try:
            robots = requests.get(f"{self.base_url}/robots.txt", timeout=10).text
            delay = None
            for line in robots.splitlines():
                if line.lower().startswith("crawl-delay"):
                    try:
                        delay = int(line.split(":", 1)[1].strip())
                    except Exception:
                        pass
            return True, (delay * 1000 if delay else None)
        except Exception:
            return True, None

    def discover(self) -> Iterable[str]:
        # Example programs page (static HTML listing for demo)
        return [f"{self.base_url}/whats-on"]

    def fetch_raw(self, url: str) -> Any:
        ok, delay_ms = self._robots_ok()
        if delay_ms:
            time.sleep(delay_ms / 1000)
        headers = {"User-Agent": "KidsSmartBot/1.0 (+https://example.org)"}
        html = None
        used = "requests+bs4"
        if settings.enable_playwright:
            try:
                html = self._fetch_with_playwright(url)
                used = "playwright"
            except Exception:
                html = None
        if html is None:
            r = requests.get(url, headers=headers, timeout=20)
            r.raise_for_status()
            html = r.text
        return {"url": url, "html": html, "robots_ok": ok, "delay_ms": delay_ms, "fetch_agent": used}

    def _fetch_with_playwright(self, url: str) -> str:
        # Lazy import to keep dependency optional
        from playwright.sync_api import sync_playwright  # type: ignore

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url, wait_until="networkidle")
            content = page.content()
            browser.close()
        return content

    def parse(self, raw: Any) -> Iterable[ProgramRecord]:
        html = raw.get("html", "")
        soup = BeautifulSoup(html, "html.parser")
        # This parser is illustrative: find event cards by common patterns
        for item in soup.select("article, .event, .event-card"):
            title = item.get_text(" ", strip=True)[:120] or "Library Program"
            link = item.find("a")
            url = link["href"] if link and link.has_attr("href") else raw.get("url")
            desc = (item.find(class_="summary") or item.find("p") or item).get_text(" ", strip=True)
            # Attempt to parse a date
            date_text = ""
            for cand in ["time", ".date", ".event-date"]:
                n = item.select_one(cand)
                if n:
                    date_text = n.get_text(" ", strip=True)
                    break
            start_dt = None
            try:
                # Very naive parse for demo
                if date_text:
                    start_dt = datetime.fromisoformat(date_text)
            except Exception:
                pass
            tags = rule_based_tags(title, desc)
            yield ProgramRecord(
                title=normalize_text(title),
                source=self.name,
                source_url=url,
                organizer="State Library Victoria",
                category=tags.category,
                start_datetime=start_dt,
                description_text=desc,
                tags=tags.tags,
                reason_tags=tags.reasons,
                snapshot_excerpt=desc[:500],
                dedupe_key_date=date_text or None,
                provenance={
                    "robots_ok": raw.get("robots_ok", True),
                    "crawl_delay_ms": raw.get("delay_ms"),
                    "fetch_agent": raw.get("fetch_agent", "requests+bs4"),
                },
            )
