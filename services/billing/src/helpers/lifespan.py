from __future__ import annotations

from typing import AsyncGenerator

import logging

from contextlib import asynccontextmanager

from aiokafka.admin import AIOKafkaAdminClient
from fastapi import FastAPI
from redis.asyncio import Redis


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:  # noqa: ARG001
    from message_broker.kafka import create_topic_if_not_exists, get_kafka_admin_client

    from core.settings import settings
    from db import redis

    # On startup events
    logging.info("Config: %s", vars(settings))

    kafka_admin_client: AIOKafkaAdminClient | None = None
    try:
        redis.redis = Redis(host=settings.redis.host, port=settings.redis.port)
        kafka_admin_client = await get_kafka_admin_client()
        await create_topic_if_not_exists(kafka_admin_client, [settings.kafka.topic_name])
        yield
    finally:
        if redis.redis:
            await redis.redis.close()
        if kafka_admin_client:
            await kafka_admin_client.close()
