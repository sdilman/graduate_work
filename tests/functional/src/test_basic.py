import pytest

from tests.functional.fixtures.fixture_basic import fixture_dummy, fixture_dummy_async


def test_dummy_sync(fixture_dummy):
    res = fixture_dummy
    assert res.get('text') == 'sync'


@pytest.mark.asyncio
async def test_dummy_async(fixture_dummy_async):
    res = await fixture_dummy_async()
    assert res.get('text') == 'async'


def test_health_check(client):
    response = client.get("/billing/api/v1/healthcheck/check")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


