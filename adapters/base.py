from __future__ import annotations
from typing import Iterable, Any
from dataclasses import dataclass
from datetime import datetime


@dataclass
class ProgramRecord:
    title: str
    source: str
    source_url: str
    organizer: str | None = None
    category: str | None = None
    subcategory: str | None = None
    start_datetime: datetime | None = None
    end_datetime: datetime | None = None
    timezone: str | None = None
    venue_name: str | None = None
    address: str | None = None
    city: str | None = None
    state: str | None = None
    country: str | None = None
    lat: float | None = None
    lon: float | None = None
    online_flag: bool | None = None
    audience_age_min: int | None = None
    audience_age_max: int | None = None
    price_amount: float | None = None
    price_currency: str | None = None
    free_flag: bool | None = None
    description_text: str | None = None
    tags: list[str] | None = None
    languages: list[str] | None = None
    provenance: dict | None = None
    reason_tags: list[str] | None = None
    snapshot_excerpt: str | None = None
    dedupe_key_date: str | None = None


class SourceAdapter:
    name: str = "base"
    base_url: str | None = None

    def discover(self) -> Iterable[str]:
        raise NotImplementedError

    def fetch_raw(self, identifier: str) -> Any:
        raise NotImplementedError

    def parse(self, raw: Any) -> Iterable[ProgramRecord]:
        raise NotImplementedError

