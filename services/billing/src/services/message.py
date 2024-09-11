from typing import Annotated

from functools import lru_cache

from aiokafka import AIOKafkaProducer
from fastapi import Depends
from message_broker.kafka import get_kafka_producer
from pydantic import BaseModel


class MessageService:
    def __init__(self, client: AIOKafkaProducer):
        self.client = client

    async def send_message(self, topic_name: str, message_model: BaseModel) -> None:
        await self.client.send_and_wait(topic=topic_name, value=message_model.model_dump_json().encode())


@lru_cache
def get_message_service(client: Annotated[AIOKafkaProducer, Depends(get_kafka_producer)]) -> MessageService:
    return MessageService(client)
