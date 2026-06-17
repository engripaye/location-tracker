import json
from typing import Any

import redis

from app.config import get_settings


class Cache:
    def __init__(self) -> None:
        redis_url = get_settings().redis_url
        self.client = redis.from_url(redis_url, decode_responses=True) if redis_url else None

    def get_json(self, key: str) -> Any | None:
        if self.client is None:
            return None
        value = self.client.get(key)
        return json.loads(value) if value else None

    def set_json(self, key: str, value: Any, ttl_seconds: int) -> None:
        if self.client is None:
            return
        self.client.setex(key, ttl_seconds, json.dumps(value, default=str))


cache = Cache()
