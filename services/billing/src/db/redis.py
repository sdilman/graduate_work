from redis.asyncio import Redis

redis: Redis | None = None  # type: ignore[type-arg]  # noqa: FA102


async def get_redis() -> Redis | None:  # type: ignore[type-arg]  # noqa: FA102
    return redis
