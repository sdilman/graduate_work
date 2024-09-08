from typing import AsyncGenerator

import logging

from contextlib import asynccontextmanager

from fastapi import FastAPI
from redis.asyncio import Redis


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:  # noqa: ARG001
    from core.settings import settings
    from db import redis

    # On startup events
    logging.info("Config: %s", vars(settings))
    redis.redis = Redis(host=settings.redis.host, port=settings.redis.port)
    logging.info("Redis: %s", str(redis))

    yield
    # On shutdown events
    await redis.close()
