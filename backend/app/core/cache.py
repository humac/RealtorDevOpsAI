import json
from typing import Any

import redis.asyncio as redis

from app.core.config import settings

redis_client = redis.from_url(settings.redis_url, decode_responses=True)


async def get_cached(key: str) -> Any | None:
    data = await redis_client.get(key)
    if data:
        return json.loads(data)
    return None


async def set_cached(key: str, value: Any, ttl: int | None = None) -> None:
    ttl = ttl or settings.cache_ttl_seconds
    await redis_client.set(key, json.dumps(value, default=str), ex=ttl)


async def invalidate_cache(pattern: str) -> None:
    keys = []
    async for key in redis_client.scan_iter(match=pattern):
        keys.append(key)
    if keys:
        await redis_client.delete(*keys)
