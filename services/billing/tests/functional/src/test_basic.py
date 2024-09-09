import pytest

from fixtures.fixture_basic import (
    fixture_dummy,  # noqa: F401
    fixture_dummy_async,
)


def test_dummy_sync(fixture_dummy) -> None:  # type: ignore  # noqa: F811, PGH003
    res = fixture_dummy
    assert res.get("text") == "sync"


@pytest.mark.asyncio
async def test_dummy_async(fixture_dummy_async) -> None:  # type: ignore  # noqa: F811, PGH003
    res = await fixture_dummy_async()
    assert res.get("text") == "async"


def test_health_check(client) -> None:  # type: ignore  # noqa: PGH003
    response = client.get("/billing/api/v1/check")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
