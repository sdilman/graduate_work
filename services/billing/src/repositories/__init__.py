from typing import Annotated

from functools import lru_cache

from fastapi import Depends

from db import get_redis
from repositories.redis import RedisService, TRedis

__all__: list[str] = ["RedisService", "get_redis_service"]


@lru_cache
def get_redis_service(redis: Annotated[TRedis, Depends(get_redis)]) -> RedisService:
    """Provider of RedisService."""
    return RedisService(redis)
