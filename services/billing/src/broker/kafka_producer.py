from typing import AsyncGenerator

from contextlib import asynccontextmanager

import backoff

from aiokafka import AIOKafkaProducer

from core.logger import get_logger
from core.settings import KafkaSettings, settings
from schemas.broker import MessageIn

logger = get_logger(__name__)


class KafkaTransactionManager:
    """Manager for Kafka transactional producer with unique transactions."""

    __slots__ = ("kafka_settings",)

    def __init__(self, kafka_settings: KafkaSettings) -> None:
        self.kafka_settings = kafka_settings

    @asynccontextmanager
    async def get_producer(self) -> AsyncGenerator[AIOKafkaProducer, None]:
        """Context manager for Kafka producer with unique transaction ID."""
        transaction_id = self.kafka_settings.generate_transaction_id()
        producer = AIOKafkaProducer(
            enable_idempotence=self.kafka_settings.enable_idempotence,
            retry_backoff_ms=self.kafka_settings.retry_backoff_ms,
            acks=self.kafka_settings.acks,
            bootstrap_servers=self.kafka_settings.bootstrap_servers,
            transactional_id=transaction_id,
        )
        await producer.start()
        logger.info("Kafka Producer started with idempotence: %s", transaction_id)
        try:
            yield producer
        finally:
            await producer.stop()
            logger.info("Kafka Producer stopped with transactional ID: %s", transaction_id)


class KafkaMessageSender:
    """Sender for Kafka messages."""

    __slots__ = ("connection_manager",)

    def __init__(self, connection_manager: KafkaTransactionManager) -> None:
        self.connection_manager = connection_manager

    @backoff.on_exception(
        backoff.expo, Exception, max_time=settings.backoff.max_time, max_tries=settings.backoff.max_tries
    )
    async def send_message(self, message: MessageIn) -> None:
        """Send message to Kafka topic."""
        async with self.connection_manager.get_producer() as producer:
            async with producer.transaction():
                await producer.send_and_wait(**message.model_dump())
                logger.info("Message sent to topic %s with idempotency key: %s", message.topic, message.key)
