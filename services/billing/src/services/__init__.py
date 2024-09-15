from typing import Annotated

from functools import lru_cache

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from db.postgres import get_pg_session
from services.order_service import OrderService

__all__: list[str] = ["OrderService", "get_order_service"]


@lru_cache
def get_order_service(db: Annotated[AsyncSession, Depends(get_pg_session)]) -> OrderService:
    return OrderService(db)
