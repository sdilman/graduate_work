from __future__ import annotations

from typing import Any

import asyncio

import asyncpg
import backoff
import redis.asyncio
import redis.exceptions

from aiokafka import AIOKafkaProducer
from aiokafka.errors import KafkaConnectionError, KafkaTimeoutError

from core.logger import get_logger
from core.settings import settings as config

logger = get_logger("services_waiter")

NOT_IMPLEMENTED = "This method should be implemented by subclasses."


class InterfaceCheckConnection:
    __slots__ = ("exception",)

    exceptions: tuple[type[Exception], ...]

    @property
    async def client(self) -> Any:
        raise NotImplementedError(NOT_IMPLEMENTED)

    async def close(self) -> None:
        raise NotImplementedError(NOT_IMPLEMENTED)

    async def perform_check(self) -> bool:
        raise NotImplementedError(NOT_IMPLEMENTED)

    async def check_connection(self) -> bool:
        try:
            return await self.perform_check()
        finally:
            await self.close()

    async def execute_check(self) -> None:
        if not await self.check_connection():
            raise self.exceptions[0](f"Condition is not met for {self.__class__.__name__}.")


class PostgresConnectionChecker(InterfaceCheckConnection):
    exceptions = (asyncpg.exceptions.PostgresError, OSError)

    @property
    async def client(self) -> Any:
        if not hasattr(self, "_client"):
            self._client = await asyncpg.connect(dsn=config.pg.dsn_pg)
        return self._client

    async def close(self) -> None:
        await (await self.client).close()

    async def perform_check(self) -> bool:
        result = await (await self.client).fetchval("SELECT 1")
        return bool(result)


class RedisConnectionChecker(InterfaceCheckConnection):
    exceptions = (redis.exceptions.RedisError,)

    @property
    async def client(self) -> Any:
        if not hasattr(self, "_client"):
            self._client = await redis.asyncio.from_url(config.redis.dsn)
        return self._client

    async def close(self) -> None:
        await (await self.client).aclose()

    async def perform_check(self) -> bool:
        result = await (await self.client).ping()
        return bool(result)


class KafkaConnectionChecker(InterfaceCheckConnection):
    exceptions = (KafkaConnectionError, KafkaTimeoutError)

    @property
    async def client(self) -> Any:
        if not hasattr(self, "_client"):
            self._client = AIOKafkaProducer(bootstrap_servers=config.kafka.bootstrap_servers)
        return self._client

    async def close(self) -> None:
        await (await self.client).stop()

    async def perform_check(self) -> bool:
        await (await self.client).start()
        result = await (await self.client).send_and_wait("test", b"ping")
        return bool(result)


class ServiceWaiter:
    __slots__ = ("checker",)

    def __init__(self, checker: InterfaceCheckConnection):
        self.checker = checker

    def get_decorator(self) -> Any:
        return backoff.on_exception(
            backoff.expo, self.checker.exceptions, max_time=config.backoff.max_time, max_tries=config.backoff.max_tries
        )

    async def wait_for_service(self) -> None:
        @self.get_decorator()
        async def execute_command() -> None:
            checker_name = self.checker.__class__.__name__
            try:
                await self.checker.execute_check()
                logger.info("%s is ready.", checker_name)
            except Exception as e:
                logger.info("%s is not ready: %s. Retrying...", checker_name, e)
                raise

        await execute_command()


async def main() -> None:
    services = [
        ServiceWaiter(PostgresConnectionChecker()),
        ServiceWaiter(RedisConnectionChecker()),
        ServiceWaiter(KafkaConnectionChecker()),
    ]

    await asyncio.gather(*(service.wait_for_service() for service in services))
    logger.info("All services are ready. Starting the application.")


if __name__ == "__main__":
    asyncio.run(main())
