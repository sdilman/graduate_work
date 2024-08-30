import logging

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi_limiter import FastAPILimiter
from redis.asyncio import Redis


@asynccontextmanager
async def lifespan(app: FastAPI):
    from src.core.api_settings import settings
    from src.db import redis_db
    from src.helpers.jaeger import configure_tracer

    # On startup events
    logging.info("Config: %s", vars(settings))
    redis_db.redis = Redis(host=settings.redis_host, port=settings.redis_port)
    await FastAPILimiter.init(redis_db.redis)

    if settings.jaeger_enable_tracer:
        configure_tracer(settings.jaeger_host, settings.jaeger_port, settings.service_name)

    yield
    # On shutdown events
    await redis_db.redis.close()
    await FastAPILimiter.close()
