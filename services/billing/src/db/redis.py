from __future__ import annotations

from redis.asyncio import Redis

redis: Redis | None = None  # type: ignore[type-arg]


async def get_redis() -> Redis | None:  # type: ignore[type-arg]
    return redis
