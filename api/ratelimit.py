from __future__ import annotations
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response, PlainTextResponse
import redis
from core.settings import settings


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        try:
            self.r = redis.Redis.from_url(settings.redis_url, decode_responses=True)
            self.r.ping()
        except Exception:
            self.r = None
        # in-memory fallback (per-process)
        self._mem_counts: dict[str, tuple[int, int]] = {}

    async def dispatch(self, request: Request, call_next):
        # Skip if redis unavailable
        ident = request.headers.get("Authorization") or (request.client.host if request.client else "anon")
        window = settings.rate_limit_per_min
        # Per-minute bucket key
        import time

        minute = int(time.time() // 60)
        key = f"rl:{ident}:{minute}"
        if self.r:
            try:
                count = self.r.incr(key)
                if count == 1:
                    self.r.expire(key, 60)
                if count > window:
                    return PlainTextResponse("Rate limit exceeded", status_code=429)
            except Exception:
                pass
        else:
            # memory fallback
            cnt, last_min = self._mem_counts.get(ident, (0, minute))
            if last_min != minute:
                cnt = 0
            cnt += 1
            self._mem_counts[ident] = (cnt, minute)
            if cnt > window:
                return PlainTextResponse("Rate limit exceeded", status_code=429)
        return await call_next(request)
