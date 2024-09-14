from db.redis import TRedis, redis_manager

__all__: list[str] = ["get_redis"]


def get_redis() -> TRedis:
    """Provide Redis client."""
    return redis_manager.get_redis()
