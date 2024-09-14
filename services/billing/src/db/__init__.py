from __future__ import annotations

from typing import Annotated

from fastapi import Depends

from db.redis import RedisManager, TRedis

__all__: list[str] = ["get_redis"]


def get_redis(redis: Annotated[RedisManager, Depends()]) -> TRedis:
    """Provide Redis client."""
    return redis.get_redis()
