from __future__ import annotations

from aiokafka import AIOKafkaProducer
from aiokafka.admin import AIOKafkaAdminClient, NewTopic

from core.logger import get_logger
from core.settings import settings

logger = get_logger(__name__)


async def get_kafka_admin_client() -> AIOKafkaAdminClient:
    admin_client = AIOKafkaAdminClient(bootstrap_servers=settings.kafka.url)
    await admin_client.start()
    return admin_client


async def get_kafka_producer() -> AIOKafkaProducer:
    producer = AIOKafkaProducer(bootstrap_servers=settings.kafka.url, retry_backoff_ms=settings.kafka.retry_backoff_ms)
    await producer.start()
    yield producer
    await producer.stop()


async def create_topic_if_not_exists(kafka_admin_client: AIOKafkaAdminClient, topic_names: list[str]) -> None:
    topics = await kafka_admin_client.list_topics()
    for topic_name in topic_names:
        if topic_name not in topics:
            new_topic = NewTopic(
                name=topic_name,
                num_partitions=settings.kafka.num_partitions,
                replication_factor=settings.kafka.replication_factor,
            )
            await kafka_admin_client.create_topics([new_topic])
            logger.info("Created new topic: %s", settings.kafka.topic_name)
        else:
            logger.info("Topic %s already exists", settings.kafka.topic_name)
