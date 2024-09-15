from typing import Annotated

from functools import lru_cache

from fastapi import Depends

from db import get_redis
from interfaces.repositories import RedisRepositoryProtocol
from repositories.redis import RedisRepository, TRedis

__all__: list[str] = ["RedisRepositoryProtocol", "get_redis_repo"]


@lru_cache
def get_redis_repo(redis: Annotated[TRedis, Depends(get_redis)]) -> RedisRepositoryProtocol:
    """Provider of RedisService."""
    return RedisRepository(redis)
