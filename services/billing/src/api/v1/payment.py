from __future__ import annotations

from typing import Annotated, cast

from fastapi import APIRouter, Depends, Request
from starlette import status

from broker import KafkaMessageSender, get_kafka_sender
from schemas.yookassa import YookassaEventNotification
from services import OrderService, PaymentService, get_order_service, get_payment_service

router = APIRouter()


@router.post(
    "/payment_create/{order_id}",
    status_code=status.HTTP_201_CREATED,
    summary="Create a payment link",
    description="Creates a payment link for the specified order.",
)
async def create_payment_link(
    request: Request, order_id: str, order_service: Annotated[OrderService, Depends(get_order_service)]
) -> str:
    link = await order_service.get_payment_link_for_order(order_id, str(request.base_url))
    return cast(str, link)


@router.post("/results_callback")
async def results_callback(
    event_notification: YookassaEventNotification,
    payment_service: Annotated[PaymentService, Depends(get_payment_service)],
    message_service: Annotated[KafkaMessageSender, Depends(get_kafka_sender)],
) -> None:
    await payment_service.process_payment_result(message_service, event_notification)
