from __future__ import annotations

from typing import cast

import uuid

from base64 import b64encode
from logging import getLogger
from urllib.parse import urljoin

import httpx

from broker import KafkaMessageSender
from core.settings import settings
from schemas.broker import MessageIn
from schemas.yookassa import YookassaEventNotification

logger = getLogger(__name__)


class PaymentService:
    _idempotency_key: str | None = None

    @property
    def idempotency_key(self) -> str:
        if self._idempotency_key is None:
            self._idempotency_key = str(uuid.uuid4().hex)
        return self._idempotency_key

    def get_headers(self) -> dict[str, str]:
        auth = b64encode(f"{settings.payment.account_id}:{settings.payment.secret_key}".encode()).decode("utf-8")

        return {
            "Authorization": f"Basic {auth}",
            "Idempotence-Key": self.idempotency_key,
            "Content-Type": "application/json",
        }

    async def create_payment_link(
        self, base_url: str, amount: float, currency: str, description: str, transaction_id: str, idempotency_key: str
    ) -> tuple[str, str]:
        self._idempotency_key = idempotency_key
        async with httpx.AsyncClient() as session:
            headers = self.get_headers()
            payment_data = {
                "amount": {"value": str(amount), "currency": currency},
                "confirmation": {
                    "type": "redirect",
                    "return_url": urljoin(
                        str(base_url), settings.payment.return_url.format(transaction_id=transaction_id)
                    ),  # TODO: transaction id and order id
                },
                "capture": "true",
                "description": description,
                "metadata": {"transaction_id": transaction_id},
            }
            logger.info("Payment data being sent: %s", payment_data)
            response = await session.post("https://api.yookassa.ru/v3/payments", headers=headers, json=payment_data)
            response.raise_for_status()
            data = response.json()
            return str(data["confirmation"]["confirmation_url"]), str(data["id"])

    async def create_refund_object(self, payment_id: str, amount: float, currency: str) -> str:
        async with httpx.AsyncClient() as session:
            headers = self.get_headers()
            refund_data = {"amount": {"value": str(amount), "currency": currency.upper()}, "payment_id": payment_id}
            response = await session.post("https://api.yookassa.ru/v3/refunds", headers=headers, json=refund_data)
            return cast(str, response.json()["id"])

    async def process_payment_result(
        self, message_service: KafkaMessageSender, event_notification: YookassaEventNotification
    ) -> None:
        try:
            await message_service.send_message(
                message=MessageIn(
                    topic=settings.kafka.topic_name,
                    key=self.idempotency_key,
                    value=event_notification.model_dump_json(),
                )
            )
        except Exception as e:  # TODO:
            logger.exception(msg=str(e))
            raise
