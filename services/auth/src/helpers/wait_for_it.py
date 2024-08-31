from typing import Any, Callable, Type

import asyncio
import logging

import asyncpg
import backoff
import redis.asyncio as aioredis
import redis.exceptions as aioredis_exceptions

from core.settings import settings as config

logger = logging.getLogger(__name__)


class ServiceWaiter:
    def __init__(
        self, client_factory: Callable[[], Any], exceptions: tuple[Type[Exception]], command: Callable[[Any], Any]
    ):
        self.client_factory = client_factory
        self.exceptions = exceptions
        self.command = command

    def get_decorator(self) -> Callable[..., Any]:
        return backoff.on_exception(
            backoff.expo, self.exceptions, max_time=config.backoff.max_time, max_tries=config.backoff.max_tries
        )

    async def wait_for_service(self) -> None:
        @self.get_decorator()
        async def execute_command() -> None:
            try:
                client = await self.client_factory()
                await self.command(client)
                logger.info("Service is ready.")
            except self.exceptions:
                logger.info("Service is not ready. Retrying...")

        await execute_command()


async def create_postgres_connection() -> asyncpg.Connection:
    return await asyncpg.connect(dsn=config.pg.dsn_pg)


async def create_redis_connection() -> aioredis.Redis:
    return aioredis.from_url(config.redis_dsn)


async def check_postgres_connection(client: asyncpg.Connection) -> None:
    await client.execute("SELECT 1")


async def check_redis_connection(client: aioredis.Redis) -> None:
    await client.ping()


async def main() -> None:
    services = [
        ServiceWaiter(
            create_postgres_connection,
            (asyncpg.exceptions.PostgresError, asyncpg.exceptions.CannotConnectNowError),
            check_postgres_connection,
        ),
        ServiceWaiter(
            create_redis_connection,
            (aioredis_exceptions.ConnectionError, aioredis_exceptions.RedisError),
            check_redis_connection,
        ),
    ]

    await asyncio.gather(*(service.wait_for_service() for service in services))
    logger.info("All services are ready. Starting the application.")


if __name__ == "__main__":
    asyncio.run(main())
