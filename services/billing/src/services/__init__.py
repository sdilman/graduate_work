from typing import Annotated

from functools import lru_cache

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from db.postgres import get_pg_session
from repositories import RedisService, get_redis_service
from services.order_service import OrderService
from services.payment import PaymentService

__all__: list[str] = ["OrderService", "get_order_service", "get_payment_service", "PaymentService"]


@lru_cache
def get_payment_service() -> PaymentService:
    return PaymentService()


@lru_cache
def get_order_service(
    db: Annotated[AsyncSession, Depends(get_pg_session)],
    redis: Annotated[RedisService, Depends(get_redis_service)],
    payment_service: Annotated[PaymentService, Depends(get_payment_service)],
) -> OrderService:
    return OrderService(db, payment_service, redis)
