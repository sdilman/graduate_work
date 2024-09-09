from __future__ import annotations

import json

from functools import lru_cache
from logging import getLogger
from urllib.parse import urljoin

import httpretty

from yookassa import Configuration, Payment

from core.settings import settings

logger = getLogger(__name__)
Configuration.account_id = settings.payment.account_id
Configuration.secret_key = settings.payment.secret_key


class PaymentService:
    @httpretty.activate
    async def create_payment_link(self, base_url: str, amount: float, currency: str, description: str) -> str:
        try:
            body_data = {"id": settings.payment.account_id, "status": "pending"}
            payment_data = {
                "amount": {"value": str(amount), "currency": currency},
                "confirmation": {"type": "redirect", "return_url": urljoin(str(base_url), settings.payment.return_url)},
                "capture": "true",
                "description": description,
            }

            httpretty.register_uri(
                httpretty.POST, "https://api.yookassa.ru/v3/payments", body=json.dumps(body_data, ensure_ascii=False)
            )

            logger.info("Payment data being sent: %s", payment_data)

            payment = Payment.create(payment_data)
        except Exception as e:  # TODO:
            logger.exception(msg=str(e))
            raise
        else:
            return str(payment.confirmation.confirmation_url)
        finally:
            self._log_request()

    def _log_request(self) -> None:
        requests = httpretty.latest_requests()
        for request in requests:
            logger.info("HTTP Request URL: %s", request.path)
            logger.info("HTTP Request Headers: %s", request.headers)
            logger.info("HTTP Request Body: %s", request.body)

    async def process_payment_callback(self) -> None:
        raise NotImplementedError


@lru_cache
def get_payment_service() -> PaymentService:
    return PaymentService()
