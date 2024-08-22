import pytest
import requests


def test_health_check():
    app_url = "http://app:8075"  # TODO: add settings
    response = requests.get(app_url + "/billing/api/v1/healthcheck/check")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}