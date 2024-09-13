from __future__ import annotations

from base64 import b64encode
from datetime import datetime
from functools import lru_cache
from logging import getLogger
from urllib.parse import urljoin
from uuid import uuid4

import httpx

from core.settings import settings
from schemas.message import PaymentResult
from services.message import MessageService

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
            return str(response.status_code)

    async def process_payment_callback(self, message_service: MessageService, transaction_id: str) -> None:
        try:
            await message_service.send_message(
                topic_name=settings.kafka.topic_name,
                message_model=PaymentResult(message=transaction_id, created_at=datetime.now()),
            )
        except Exception as e:  # TODO:
            logger.exception(msg=str(e))
            raise


@lru_cache
def get_payment_service() -> PaymentService:
    return PaymentService()
