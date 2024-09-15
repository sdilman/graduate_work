from __future__ import annotations

from typing import Any, Awaitable, Callable, TypeAlias, cast

import backoff

from redis.asyncio import Redis
from redis.exceptions import ConnectionError, ResponseError, TimeoutError

from core.settings import settings
from interfaces.repositories import RedisRepositoryProtocol
from schemas.cache import CacheFlushDto, CacheReadDto, CacheSetDto, CacheUpdateDto

TDecorator: TypeAlias = Callable[[Callable[..., Awaitable[Any]]], Callable[..., Awaitable[Any]]]
TRedis: TypeAlias = "Redis[str]"


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


class RedisRepository(RedisRepositoryProtocol):
    def __init__(self, redis: TRedis):
        self.redis = redis

    @redis_backoff_decorator()
    async def create(self, dto: CacheSetDto) -> None:
        await self.redis.setex(**dto.model_dump())

    @redis_backoff_decorator()
    async def read(self, dto: CacheReadDto) -> str | None:
        value: str | None = await self.redis.get(**dto.model_dump())
        return value

    @redis_backoff_decorator()
    async def update(self, dto: CacheUpdateDto) -> None:
        await self.redis.expire(**dto.model_dump())

    @redis_backoff_decorator()
    async def delete(self, dto: CacheFlushDto) -> None:
        await self.update(dto)
