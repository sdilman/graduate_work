import asyncio

import pytest_asyncio

pytest_plugins = [
    "fixtures.redis_fixtures",
    "fixtures.client_fixtures",
    "fixtures.pg_fixtures",
    "fixtures.jwt_fixtures",
]


@pytest_asyncio.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()
