import os
from dataclasses import dataclass
from functools import lru_cache

try:
    from dotenv import load_dotenv
except ModuleNotFoundError:
    load_dotenv = None


if load_dotenv is not None:
    load_dotenv()


@dataclass(frozen=True)
class Settings:
    database_url: str
    redis_url: str | None
    jwt_secret_key: str
    jwt_algorithm: str
    access_token_minutes: int
    refresh_token_days: int
    share_link_hours: int
    google_maps_api_key: str | None
    nominatim_user_agent: str
    cors_origins: str


@lru_cache
def get_settings() -> Settings:
    return Settings(
        database_url=os.getenv(
            "DATABASE_URL",
            "sqlite:///./location_tracker.db",
        ),
        redis_url=os.getenv("REDIS_URL"),
        jwt_secret_key=os.getenv("JWT_SECRET_KEY", "change-me-in-production"),
        jwt_algorithm=os.getenv("JWT_ALGORITHM", "HS256"),
        access_token_minutes=_env_int("ACCESS_TOKEN_MINUTES", 15),
        refresh_token_days=_env_int("REFRESH_TOKEN_DAYS", 30),
        share_link_hours=_env_int("SHARE_LINK_HOURS", 24),
        google_maps_api_key=os.getenv("GOOGLE_MAPS_API_KEY"),
        nominatim_user_agent=os.getenv("NOMINATIM_USER_AGENT", "location-tracker/1.0"),
        cors_origins=os.getenv("CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173"),
    )


def _env_int(name: str, default: int) -> int:
    raw_value = os.getenv(name)
    if raw_value is None:
        return default
    try:
        return int(raw_value)
    except ValueError:
        return default
