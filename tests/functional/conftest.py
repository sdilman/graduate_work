import pytest
import pytest_asyncio

from fastapi.testclient import TestClient

from src.main import app


@pytest.fixture
def client():
    return TestClient(app)

