from __future__ import annotations

from typing import Annotated, cast

from fastapi import APIRouter, Depends, HTTPException, Request

from broker import KafkaMessageSender, get_kafka_sender
from schemas.youkassa import YoukassaEventNotification
from services import OrderService, PaymentService, get_order_service, get_payment_service

router = APIRouter()


@router.post("/payment_create/{order_id}")
async def create_payment_link(
    order_id: str, request: Request, order_service: Annotated[OrderService, Depends(get_order_service)]
) -> str:
    order = await order_service.get_order(order_id)
    if order is None:
        raise HTTPException(status_code=404, detail=f"Order with id={order_id} not found")

    try:
        link = await order_service.get_payment_link_for_order(order.id, str(request.base_url))
    except Exception as e:
        raise HTTPException(status_code=500) from e
    return cast(str, link)


@router.post("/results_callback")
async def results_callback(
    event_notification: YoukassaEventNotification,
    payment_service: Annotated[PaymentService, Depends(get_payment_service)],
    message_service: Annotated[KafkaMessageSender, Depends(get_kafka_sender)],
) -> None:
    await payment_service.process_payment_result(message_service, event_notification)
