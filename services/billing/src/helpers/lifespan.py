from typing import AsyncGenerator

from contextlib import asynccontextmanager

from fastapi import FastAPI


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncGenerator[None, None]:
    from broker import initialize_kafka_topics
    from db.redis import redis_manager as redis

    try:
        await redis.initialize()
        await initialize_kafka_topics()
        yield
    finally:
        await redis.close()
