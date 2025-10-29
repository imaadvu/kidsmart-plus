from __future__ import annotations
from .base import SourceAdapter, ProgramRecord
from core.settings import settings
from core.nlp import rule_based_tags, normalize_text
import requests
import requests_cache
from datetime import datetime
from typing import Iterable, Any


requests_cache.install_cache("meetup_cache", expire_after=3600)


class MeetupAdapter(SourceAdapter):
    name = "meetup"
    base_url = "https://api.meetup.com"

    def discover(self) -> Iterable[str]:
        # Demo: public events search endpoint would require OAuth; keep illustrative
        return ["find/upcoming_events?topic_category=education"]

    def fetch_raw(self, identifier: str) -> Any:
        token = settings.meetup_token
        headers = {"Authorization": f"Bearer {token}"} if token else {}
        url = f"{self.base_url}/{identifier}"
        r = requests.get(url, headers=headers, timeout=20)
        r.raise_for_status()
        return r.json()

    def parse(self, raw: Any) -> Iterable[ProgramRecord]:
        events = raw.get("events", []) if isinstance(raw, dict) else []
        for e in events:
            title = e.get("name") or "Untitled"
            desc = e.get("description") or ""
            url = e.get("link") or ""
            start_ms = e.get("time")
            start_dt = datetime.utcfromtimestamp(start_ms / 1000) if start_ms else None
            tags = rule_based_tags(title, desc)
            venue = (e.get("venue") or {})
            yield ProgramRecord(
                title=normalize_text(title),
                source=self.name,
                source_url=url,
                organizer=(e.get("group") or {}).get("name"),
                category=tags.category,
                start_datetime=start_dt,
                city=venue.get("city"),
                lat=venue.get("lat"),
                lon=venue.get("lon"),
                description_text=desc,
                tags=tags.tags,
                reason_tags=tags.reasons,
                dedupe_key_date=start_dt.isoformat() if start_dt else None,
                provenance={"fetch_agent": "meetup_api"},
            )
