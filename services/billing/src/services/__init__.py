from typing import Annotated

from functools import lru_cache

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from db.postgres import get_pg_session
from interfaces.repositories import RedisRepositoryProtocol
from repositories import get_redis_repo
from services.entity import EntityService
from services.order_service import OrderService
from services.payment import PaymentService
from services.product_service import ProductService

__all__: list[str] = [
    "OrderService",
    "get_order_service",
    "EntityService",
    "get_entity_service",
    "ProductService",
    "get_product_service",
]


@lru_cache
def get_payment_service() -> PaymentService:
    """Provider of PaymentService."""
    return PaymentService()


@lru_cache
def get_order_service(
    db: Annotated[AsyncSession, Depends(get_pg_session)],
    redis_repo: Annotated[RedisRepositoryProtocol, Depends(get_redis_repo)],
    payment_service: Annotated[PaymentService, Depends(get_payment_service)],
) -> OrderService:
    """Provider of OrderService."""
    return OrderService(db, redis_repo, payment_service)


@lru_cache
def get_entity_service(db: Annotated[AsyncSession, Depends(get_pg_session)]) -> EntityService:
    """Provider of EntityService."""
    return EntityService(db)


@lru_cache
def get_product_service(db: Annotated[AsyncSession, Depends(get_pg_session)]) -> ProductService:
    """Provider of ProductService."""
    return ProductService(db)
