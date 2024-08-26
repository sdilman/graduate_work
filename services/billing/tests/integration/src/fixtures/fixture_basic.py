from __future__ import annotations

from typing import Any, Callable, Coroutine

import pytest
import pytest_asyncio


@pytest.fixture
def fixture_dummy() -> dict[str, str]:
    return {"text": "sync"}


@pytest_asyncio.fixture
def fixture_dummy_async() -> Callable[[], Coroutine[Any, Any, dict[str, str]]]:
    async def inner() -> dict[str, str]:
        return {"text": "async"}

    return inner
