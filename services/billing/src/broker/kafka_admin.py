from aiokafka.admin import AIOKafkaAdminClient, NewTopic

from broker.topics import KafkaTopicsConfig
from core.logger import get_logger
from core.settings import settings

logger = get_logger(__name__)


class KafkaAdminManager:
    """Manager for Kafka Admin Client."""

    __slots__ = ("bootstrap_servers", "admin_client")

    def __init__(self, bootstrap_servers: str):
        self.bootstrap_servers = bootstrap_servers
        self.admin_client: AIOKafkaAdminClient | None = None

    async def start(self) -> None:
        """Initialize Kafka Admin Client."""
        self.admin_client = AIOKafkaAdminClient(bootstrap_servers=self.bootstrap_servers)
        await self.admin_client.start()
        logger.info("Kafka Admin Client started")

    async def stop(self) -> None:
        """Close Kafka Admin Client."""
        if self.admin_client:
            await self.admin_client.close()
            logger.info("Kafka Admin Client stopped")

    async def create_topics(self, topics_config: KafkaTopicsConfig) -> None:
        """Create topics based on configuration."""
        if not self.admin_client:
            raise RuntimeError("Kafka admin client is not initialized")

        existing_topics = await self.admin_client.list_topics()

        new_topics = [
            NewTopic(
                name=topic.name,
                num_partitions=topic.num_partitions,
                replication_factor=topic.replication_factor,
                topic_configs=topic.config,
            )
            for topic in topics_config.topics
            if topic.name not in existing_topics
        ]

        if new_topics:
            await self.admin_client.create_topics(new_topics)
            logger.info("Created topics: %s", [topic.name for topic in new_topics])
        else:
            logger.info("No new topics to create, all topics already exist")


async def initialize_kafka_topics() -> None:
    kafka_admin_manager = KafkaAdminManager(bootstrap_servers=settings.kafka.bootstrap_servers)
    kafka_topics_config = KafkaTopicsConfig.load_from_file()

    await kafka_admin_manager.start()
    try:
        await kafka_admin_manager.create_topics(kafka_topics_config)
    finally:
        await kafka_admin_manager.stop()
