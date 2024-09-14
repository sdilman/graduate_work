from __future__ import annotations

from typing import Any

import json

from pathlib import Path

from pydantic import BaseModel, Field

from core.settings import settings


class TopicConfig(BaseModel):
    name: str = Field(..., description="Name of the Kafka topic")
    num_partitions: int = Field(..., description="Number of partitions for the topic")
    replication_factor: int = Field(..., description="Replication factor for the topic")
    config: dict[str, Any] = Field(default_factory=dict, description="Additional topic configuration")


class KafkaTopicsConfig(BaseModel):
    topics: list[TopicConfig] = Field(..., description="List of Kafka topics configurations")

    @staticmethod
    def load_from_file() -> "KafkaTopicsConfig":
        """Load Kafka topics config from a JSON file."""

        with Path.open(settings.kafka.config_path, encoding="utf-8") as conf:
            data = json.load(conf)
        return KafkaTopicsConfig(**data)
