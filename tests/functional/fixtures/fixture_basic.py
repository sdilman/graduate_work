import pytest
import pytest_asyncio


@pytest.fixture
def fixture_dummy():
    data = {'text': 'sync'}
    return data


@pytest_asyncio.fixture
def fixture_dummy_async():
    async def inner():
        data = {'text': 'async'}
        return data
    return inner