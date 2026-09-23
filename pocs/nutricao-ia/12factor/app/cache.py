"""
Factor IV: Redis tratado como backing service anexado via REDIS_URL.
Processos não guardam cache em memória local — Factor VI (stateless).
"""
from redis.asyncio import Redis, from_url
from app.config import settings
from functools import lru_cache


@lru_cache
def get_redis_client() -> Redis:
    return from_url(settings.REDIS_URL, decode_responses=True)


async def cache_get(key: str) -> str | None:
    client = get_redis_client()
    return await client.get(key)


async def cache_set(key: str, value: str, ttl_seconds: int = 3600) -> None:
    client = get_redis_client()
    await client.setex(key, ttl_seconds, value)


async def cache_delete(key: str) -> None:
    client = get_redis_client()
    await client.delete(key)