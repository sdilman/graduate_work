import asyncio

import backoff
import httpx

from core.settings import settings as config


async def check(session: httpx.AsyncClient) -> None:
    response = await session.get(config.app.base_url + config.app.health_check_path)
    if response.status_code != 200:
        raise httpx.HTTPStatusError("App is not available. Backoff...", request=response.request, response=response)


@backoff.on_exception(backoff.expo, (httpx.HTTPStatusError, httpx.ConnectError), max_time=60, max_tries=50)
async def wait_for_app() -> None:
    async with httpx.AsyncClient() as session:
        await check(session)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(wait_for_app())
    finally:
        loop.close()
