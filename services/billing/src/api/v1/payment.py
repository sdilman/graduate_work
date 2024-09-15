from __future__ import annotations

from typing import Annotated

from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from broker import KafkaMessageSender, get_kafka_sender
from core.settings import settings
from db.postgres import get_pg_session
from repositories import RedisService, get_redis_service
from schemas.broker import MessageIn
from schemas.entity import TransactionSchema, TransactionStatusSchema, TransactionTypeSchema
from schemas.youkassa import YoukassaEventNotification
from services.entity import EntityService, get_entity_service
from services.payment import PaymentService, get_payment_service

router = APIRouter()


@router.post("/payment_create/{order_id}")
async def create_payment_link(
    order_id: str,
    request: Request,
    entity_service: Annotated[EntityService, Depends(get_entity_service)],
    payment: Annotated[PaymentService, Depends(get_payment_service)],
    redis: Annotated[RedisService, Depends(get_redis_service)],
    db: Annotated[AsyncSession, Depends(get_pg_session)],
) -> tuple[str, str]:
    order = await entity_service.get_order(db, order_id)
    if order is None:
        raise HTTPException(status_code=404, detail=f"Order with id={order_id} not found")

    try:
        ts = TransactionSchema(
            order_id=order_id,
            type=TransactionTypeSchema.PAYMENT,
            status=TransactionStatusSchema.PENDING,
            amount=order.total_amount,
            currency=order.currency,
        )
        transaction_id: str = await entity_service.create_transaction(db, ts)
        idempotence_key: str = str(uuid4())
        link: str
        cache_key = await redis.get_cache_key(order_id=order_id)
        cached_link = await redis.get_value_by_key(key=cache_key)
        if cached_link:
            await redis.refresh_payment_link(key=cache_key)
            link = cached_link
        else:
            link = await payment.create_payment_link(
                base_url=request.base_url,
                amount=order.total_amount,
                currency=order.currency.value.upper(),
                description="",
                transaction_id=transaction_id,
                idempotence_key=idempotence_key,
            )
            await redis.save_payment_link(order_id=order_id, payment_link=link)

    except Exception as e:
        raise HTTPException(status_code=500) from e
    else:
        return link, transaction_id


@router.get("/payment_create_callback/{transaction_id}")
async def payment_callback(
    transaction_id: str,
    payment: Annotated[PaymentService, Depends(get_payment_service)],
    message: Annotated[KafkaMessageSender, Depends(get_kafka_sender)],
) -> None:
    await payment.process_payment_callback(message, transaction_id)


@router.post("/results_callback")
async def results_callback(
    event_notification: YoukassaEventNotification,
    message_service: Annotated[KafkaMessageSender, Depends(get_kafka_sender)],
) -> None:
    await message_service.send_message(
        message=MessageIn(topic=settings.kafka.topic_name, key="idempotency_key", value=event_notification)
    )
