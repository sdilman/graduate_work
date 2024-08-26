import requests  # type: ignore # noqa: PGH003

from core.settings import settings


def test_health_check() -> None:
    url = settings.app.base_url + settings.app.health_check_path
    response = requests.get(url, timeout=5)
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
