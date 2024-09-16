from typing import Any

import asyncio

import httpx

from core.logger import get_logger
from core.settings import settings
from helpers.wait_for_services import InterfaceCheckConnection, ServiceWaiter

logger = get_logger("app_waiter")


class AppConnectionChecker(InterfaceCheckConnection):
    exceptions = (httpx.ConnectError, httpx.ConnectTimeout)

    @property
    async def client(self) -> Any:
        if not hasattr(self, "_client"):
            self._client = httpx.AsyncClient()
        return self._client

    async def close(self) -> None:
        if hasattr(self, "_client"):
            await self._client.aclose()
            del self._client

    async def perform_check(self) -> bool:
        client = await self.client
        url = f"{settings.app.base_url}{settings.app.health_check_path}"
        response = await client.get(url=url)
        return bool(response.status_code == 200)


async def main() -> None:
    services = [ServiceWaiter(AppConnectionChecker())]

    await asyncio.gather(*(service.wait_for_service() for service in services))
    logger.info("App is ready. Starting the workers.")


if __name__ == "__main__":
    asyncio.run(main())
