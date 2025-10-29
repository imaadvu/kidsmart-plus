from pydantic_settings import BaseSettings
from pydantic import field_validator
from typing import List
import os


class Settings(BaseSettings):
    app_env: str = os.getenv("APP_ENV", "development")
    secret_key: str = "change-me"
    jwt_algo: str = "HS256"

    db_url: str | None = None
    db_url_sqlite: str = "sqlite:///./kidssmart_dev.db"

    redis_url: str = "redis://localhost:6379/0"

    eventbrite_token: str | None = None
    meetup_token: str | None = None
    serpapi_key: str | None = None

    maps_token: str | None = None

    enable_playwright: bool = False
    enable_embeddings: bool = False

    allowed_origins: List[str] = ["http://localhost:3000", "http://localhost:8501"]

    rate_limit_per_min: int = 120
    cache_ttl: int = int(os.getenv("CACHE_TTL", 60))
    admin_username: str = os.getenv("ADMIN_USERNAME", "admin")
    admin_password: str = os.getenv("ADMIN_PASSWORD", "change-me")
    neardup_threshold: float = float(os.getenv("NEARDUP_THRESHOLD", 0.85))
    geocoding_enabled: bool = os.getenv("GEOCODING_ENABLED", "false").lower() == "true"

    @property
    def sqlalchemy_url(self) -> str:
        return self.db_url or self.db_url_sqlite

    @field_validator("allowed_origins", mode="before")
    @classmethod
    def split_origins(cls, v):
        if isinstance(v, str):
            return [s.strip() for s in v.split(",") if s.strip()]
        return v


settings = Settings()  # type: ignore[arg-type]
