from __future__ import annotations
from typing import Optional, Tuple
from geopy.geocoders import Nominatim
from functools import lru_cache
from core.settings import settings


@lru_cache(maxsize=1024)
def geocode_address_cached(addr: str) -> Optional[Tuple[float, float]]:
    if not settings.geocoding_enabled:
        return None
    try:
        g = Nominatim(user_agent="kidssmart")
        loc = g.geocode(addr, timeout=10)
        if not loc:
            return None
        return (loc.latitude, loc.longitude)
    except Exception:
        return None

