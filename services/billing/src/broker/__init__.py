from typing import Annotated

from functools import lru_cache

from fastapi import Depends

from broker.kafka_admin import KafkaAdminManager, initialize_kafka_topics
from broker.kafka_producer import KafkaMessageSender, KafkaTransactionManager
from core.settings import KafkaSettings, get_settings

__all__ = [
    "initialize_kafka_topics",
    "KafkaAdminManager",
    "KafkaTransactionManager",
    "KafkaMessageSender",
    "get_kafka_sender",
]


@lru_cache
def get_kafka_producer(kafka_settings: Annotated[KafkaSettings, Depends(get_settings)]) -> KafkaTransactionManager:
    """Provide Kafka transactional producer."""
    return KafkaTransactionManager(kafka_settings)


@lru_cache
def get_kafka_sender(
    connection_manager: Annotated[KafkaTransactionManager, Depends(get_kafka_producer)],
) -> KafkaMessageSender:
    """Provide Kafka message sender."""
    return KafkaMessageSender(connection_manager)
