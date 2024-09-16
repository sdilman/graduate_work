import requests  # type: ignore # noqa: PGH003

import pytest

import traceback
import logging

from core.settings import settings


logger = logging.getLogger(__name__)


def test_payment() -> None:
    # Register user
    user_url = settings.auth.base_url + settings.auth.register_user_path
    user_data = {"email": "binge-watcher@example.com", "password": "pwd123", "request_password_change": "false"}
    response = requests.post(url=user_url, json=user_data)
    assert response.status_code == 201
    user_id = response.json()["user_id"]

    # Login user (create cookie with token)
    user_login_url = settings.auth.base_url + settings.auth.login_user_path
    user_login_data = {"email": "binge-watcher@example.com", "password": "pwd123"}
    response = requests.post(url=user_login_url, json=user_login_data)
    assert response.status_code == 200
    auth_token_value = response.headers["authorization"][len("Bearer") + 1 :]

    # Product
    product_url = settings.app.base_url + settings.app.create_product_path
    product_data = {
        "title": "Subscription Ultra",
        "description": "Subscription for all films",
        "basic_price": 5000,
        "basic_currency": "rub",
    }
    response = requests.post(url=product_url, json=product_data, cookies={settings.auth.access_name: auth_token_value})
    assert response.status_code == 201
    product_id = str(response.json())

    # Order
    order_url = settings.app.base_url + settings.app.create_order_path
    order_data = {
        "idempotency_key": "any_unique_identifier",
        "user_id": user_id,
        "status": "pending",
        "currency": "rub",
        "products_id": [product_id],
        "total_amount": 5000,
    }

    response = requests.post(url=order_url, json=order_data, cookies={settings.auth.access_name: auth_token_value})
    assert response.status_code == 201
    order_id = str(response.json())

    # Payment
    payment_url_mask = settings.app.base_url + settings.app.create_payment_link_path
    payment_url = payment_url_mask.format(order_id=order_id)
    payment_data = {}
    try:
        response = requests.post(
            url=payment_url, json=payment_data, cookies={settings.auth.access_name: auth_token_value}
        )
        response.raise_for_status()
        assert response.status_code == 201
    except requests.exceptions.RequestException as e:
        logger.error("Request failed: %s", traceback.format_exc())
        raise


@pytest.mark.skip
def test_payment_callback() -> None:
    # Payment callback
    transaction_id = "00000000-0000-0000-0000-000000000001"
    payment_callback_url = settings.app.base_url + settings.app.payment_callback_path.format(
        transaction_id=transaction_id
    )
    try:
        response = requests.get(url=payment_callback_url)
        response.raise_for_status()
        assert response.status_code == 200
    except requests.exceptions.RequestException as e:
        logger.error("Request failed: %s", traceback.format_exc())
        raise
