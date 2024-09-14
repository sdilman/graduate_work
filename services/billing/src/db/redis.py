from __future__ import annotations

from typing import TypeAlias

from redis.asyncio import Redis
from redis.exceptions import ConnectionError as RedisConnectionError

from core.logger import get_logger
from core.settings import settings

logger = get_logger(__name__)

TRedis: TypeAlias = "Redis[bytes]"


class RedisManager:
    __slots__ = ("redis",)

    def __init__(self) -> None:
        self.redis: TRedis | None = None

    async def initialize(self) -> None:
        """Initialize redis connection."""
        if self.redis is None:
            self.redis = Redis(host=settings.redis.host, port=settings.redis.port)
            logger.info("Redis client has been initialized")

    async def close(self) -> None:
        """Close redis connection."""
        if self.redis:
            await self.redis.aclose()  # type: ignore[attr-defined]
            logger.info("Redis client has been closed")

    def get_redis(self) -> TRedis:
        """Get redis client."""
        if self.redis is None:
            raise RedisConnectionError("Redis client has not been initialized.")
        return self.redis


redis_manager = RedisManager()
