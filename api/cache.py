"""Simple in-memory cache for API responses."""
import json
from typing import Any, Optional
from datetime import datetime, timedelta


class Cache:
    """Simple in-memory cache with TTL support."""
    
    def __init__(self):
        self._cache = {}
    
    def get_json(self, key: str) -> Optional[Any]:
        """Get a value from cache as JSON."""
        if key in self._cache:
            value, expiry = self._cache[key]
            if datetime.utcnow() < expiry:
                return value
            else:
                # Expired, remove it
                del self._cache[key]
        return None
    
    def set_json(self, key: str, value: Any, ttl: int = 60):
        """Set a value in cache with TTL in seconds."""
        expiry = datetime.utcnow() + timedelta(seconds=ttl)
        self._cache[key] = (value, expiry)
    
    def clear(self):
        """Clear all cache entries."""
        self._cache.clear()


# Global cache instance
cache = Cache()

