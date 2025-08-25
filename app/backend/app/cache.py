import os
import redis

REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_DB = int(os.getenv("REDIS_DB", "0"))

r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, decode_responses=True)


import json
import os
from typing import Optional

try:
    import redis  # type: ignore
except Exception:
    redis = None  # optional dependency


class _InMemory:
    def __init__(self):
        self._store = {}

    def exists(self, key: str) -> int:
        return 1 if key in self._store else 0

    def get(self, key: str) -> Optional[str]:
        item = self._store.get(key)
        if not item:
            return None
        value, expires_at = item
        if expires_at is not None and expires_at < __import__("time").time():
            self._store.pop(key, None)
            return None
        return value

    def setex(self, key: str, ttl: int, value: str) -> None:
        self._store[key] = (value, __import__("time").time() + ttl)


if redis and REDIS_HOST:
    _r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, decode_responses=True)
    # light wrapper to provide exists/get/setex APIs returning str like in Redis-py
    class _RedisWrapper:
        def exists(self, key: str) -> int:
            return int(_r.exists(key))
        def get(self, key: str):
            v = _r.get(key)
            return v.decode("utf-8") if isinstance(v, (bytes, bytearray)) else v
        def setex(self, key: str, ttl: int, value: str):
            _r.setex(key, ttl, value)
    r = _RedisWrapper()
else:
    r = _InMemory()
