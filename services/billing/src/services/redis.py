from typing import Annotated

from functools import lru_cache

import backoff
import requests

from fastapi import Depends
from redis.asyncio import Redis

from core.settings import settings
from db.redis import get_redis

BACKOFF_SETTINGS = {
    "wait_gen": backoff.expo,
    "exception": (requests.exceptions.ConnectionError, requests.exceptions.HTTPError, requests.exceptions.Timeout),
    "max_time": settings.redis.backoff_max_time,
    "max_tries": settings.redis.backoff_max_tries,
}


class RedisService:
    def __init__(self, redis: Redis):  # type: ignore[type-arg]
        self.redis = redis

    @staticmethod
    async def get_cache_key(order_id: str) -> str:
        return order_id

    @backoff.on_exception(**BACKOFF_SETTINGS)
    async def save_payment_link(
        self, order_id: str, payment_link: str, expire_time_sec: int = settings.redis.record_expiration_time
    ) -> None:
        key = await self.get_cache_key(order_id)
        await self.redis.setex(name=key, value=payment_link, time=expire_time_sec)

    @backoff.on_exception(**BACKOFF_SETTINGS)
    async def del_payment_link(self, order_id: str) -> None:
        key = await self.get_cache_key(order_id)
        await self.redis.expire(name=key, time=0)

    @backoff.on_exception(**BACKOFF_SETTINGS)
    async def refresh_payment_link(
        self, key: str, expire_time_sec: int = settings.redis.record_expiration_time
    ) -> None:
        key = await self.get_cache_key(key)
        await self.redis.expire(name=key, time=expire_time_sec)

    @backoff.on_exception(**BACKOFF_SETTINGS)
    async def get_value_by_key(self, key: str) -> str | None:  # noqa: FA102
        value = await self.redis.get(name=key)
        if value:
            return str(value)
        return None


@lru_cache
def get_redis_service(redis: Annotated[Redis, Depends(get_redis)]) -> RedisService:  # type: ignore[type-arg]
    return RedisService(redis)
