from __future__ import annotations

from typing import Any

import asyncio

import backoff
import httpx

from core.logger import get_logger
from core.settings import settings as config

logger = get_logger("services_waiter")


class InterfaceCheckConnection:
    __slots__ = ("exception",)

    exceptions: tuple[type[Exception], ...]

    async def check_connection(self) -> bool:
        raise NotImplementedError("This method should be implemented by subclasses.")

    async def execute_check(self) -> None:
        if not await self.check_connection():
            raise self.exceptions[0](f"Condition is not met for {self.__class__.__name__}.")


class AppConnectionChecker(InterfaceCheckConnection):
    exceptions = (httpx.ConnectError,)

    async def check_connection(self) -> bool:
        async with httpx.AsyncClient() as session:
            response = await session.get(config.app.base_url + config.app.health_check_path)
            return response.status_code == 200


class AuthConnectionChecker(InterfaceCheckConnection):
    exceptions = (httpx.ConnectError,)

    async def check_connection(self) -> bool:
        async with httpx.AsyncClient() as session:
            response = await session.get(config.auth.base_url + config.auth.health_check_path)
            return response.status_code == 200


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
    services = [ServiceWaiter(AppConnectionChecker()), ServiceWaiter(AuthConnectionChecker())]

    await asyncio.gather(*(service.wait_for_service() for service in services))
    logger.info("All services are ready. Starting the application.")


if __name__ == "__main__":
    asyncio.run(main())
