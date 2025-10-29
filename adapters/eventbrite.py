from __future__ import annotations
from .base import SourceAdapter, ProgramRecord
from core.settings import settings
from core.nlp import rule_based_tags, compute_dedupe_hash, normalize_text
import requests
import requests_cache
from datetime import datetime
from typing import Iterable, Any


requests_cache.install_cache("eventbrite_cache", expire_after=3600)


class EventbriteAdapter(SourceAdapter):
    name = "eventbrite"
    base_url = "https://www.eventbriteapi.com/v3"

    def discover(self) -> Iterable[str]:
        # For demo: return a small set of event search queries or organization IDs
        return ["events/search?q=reading", "events/search?q=children"]

    def fetch_raw(self, identifier: str) -> Any:
        token = settings.eventbrite_token
        headers = {"Authorization": f"Bearer {token}"} if token else {}
        url = f"{self.base_url}/{identifier}"
        resp = requests.get(url, headers=headers, timeout=20)
        resp.raise_for_status()
        return resp.json()

    def parse(self, raw: Any) -> Iterable[ProgramRecord]:
        # Eventbrite search results format
        events = raw.get("events", []) if isinstance(raw, dict) else []
        for e in events:
            title = e.get("name", {}).get("text") or "Untitled"
            description = (e.get("description", {}) or {}).get("text") or ""
            url = e.get("url") or e.get("resource_uri") or ""
            start = e.get("start", {})
            end = e.get("end", {})
            start_dt = datetime.fromisoformat(start.get("utc").replace("Z", "+00:00")) if start.get("utc") else None
            end_dt = datetime.fromisoformat(end.get("utc").replace("Z", "+00:00")) if end.get("utc") else None
            tz = start.get("timezone")
            tags = rule_based_tags(title, description)
            yield ProgramRecord(
                title=normalize_text(title),
                source=self.name,
                source_url=url,
                organizer=(e.get("organizer", {}) or {}).get("name"),
                category=tags.category,
                start_datetime=start_dt,
                end_datetime=end_dt,
                timezone=tz,
                online_flag=e.get("online_event") or tags.online_flag,
                description_text=description,
                price_amount=None,
                free_flag=tags.free_flag,
                tags=tags.tags,
                reason_tags=tags.reasons,
                dedupe_key_date=(start.get("local") or start.get("utc")),
                provenance={"fetch_agent": "eventbrite_api"},
            )
