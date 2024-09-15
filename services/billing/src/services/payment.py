from __future__ import annotations

from base64 import b64encode
from functools import lru_cache
from logging import getLogger
from urllib.parse import urljoin
from uuid import uuid4

import httpx

from broker import KafkaMessageSender
from core.settings import settings
from schemas.broker import MessageIn
from schemas.youkassa import YoukassaEventNotification

logger = getLogger(__name__)


class PaymentService:
    async def create_payment_link(
        self, base_url: str, amount: float, currency: str, description: str, transaction_id: str, idempotence_key: str
    ) -> str:
        async with httpx.AsyncClient() as session:
            idempotence_key = str(uuid4())
            auth = b64encode(f"{settings.payment.account_id}:{settings.payment.secret_key}".encode()).decode("utf-8")
            headers = {
                "Authorization": f"Basic {auth}",
                "Idempotence-Key": idempotence_key,
                "Content-Type": "application/json",
            }
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
            }
            logger.info("Payment data being sent: %s", payment_data)
            response = await session.post("https://api.yookassa.ru/v3/payments", headers=headers, json=payment_data)
            response.raise_for_status()
            data = response.json()
            return str(data["confirmation"]["confirmation_url"])

    async def process_payment_result(
        self, message_service: KafkaMessageSender, event_notification: YoukassaEventNotification
    ) -> None:
        try:
            await message_service.send_message(
                message=MessageIn(topic=settings.kafka.topic_name, key="idempotency_key", value=event_notification)
            )
        except Exception as e:  # TODO:
            logger.exception(msg=str(e))
            raise


@lru_cache
def get_payment_service() -> PaymentService:
    return PaymentService()
