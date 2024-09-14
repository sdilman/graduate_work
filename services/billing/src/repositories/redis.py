from __future__ import annotations

from typing import Any, Awaitable, Callable, TypeAlias, cast

import backoff

from redis.asyncio import Redis
from redis.exceptions import ConnectionError, ResponseError, TimeoutError

from core.settings import settings

TDecorator: TypeAlias = Callable[[Callable[..., Awaitable[Any]]], Callable[..., Awaitable[Any]]]
TRedis: TypeAlias = "Redis[bytes]"


def redis_backoff_decorator() -> TDecorator:
    return cast(
        TDecorator,
        backoff.on_exception(
            wait_gen=backoff.expo,
            exception=(ConnectionError, ResponseError, TimeoutError),
            max_time=settings.redis.backoff_max_time,
            max_tries=settings.redis.backoff_max_tries,
        ),
    )


class RedisService:
    def __init__(self, redis: TRedis):
        self.redis = redis

    @staticmethod
    async def get_cache_key(order_id: str) -> str:
        return order_id

    @redis_backoff_decorator()
    async def save_payment_link(
        self, order_id: str, payment_link: str, expire_time_sec: int = settings.redis.record_expiration_time
    ) -> None:
        key = await self.get_cache_key(order_id)
        await self.redis.setex(name=key, value=payment_link, time=expire_time_sec)

    @redis_backoff_decorator()
    async def del_payment_link(self, order_id: str) -> None:
        key = await self.get_cache_key(order_id)
        await self.redis.expire(name=key, time=0)

    @redis_backoff_decorator()
    async def refresh_payment_link(
        self, key: str, expire_time_sec: int = settings.redis.record_expiration_time
    ) -> None:
        key = await self.get_cache_key(key)
        await self.redis.expire(name=key, time=expire_time_sec)

    @redis_backoff_decorator()
    async def get_value_by_key(self, key: str) -> str | None:
        value = await self.redis.get(name=key)
        if value:
            return str(value)
        return None
