from __future__ import annotations

from typing import Annotated, Any, cast

from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from db.postgres import get_pg_session
from schemas.entity import OrderSchema
from services.order_service import get_order_service

router = APIRouter()


@router.post("/create_order")
async def create_order(
    request: Request, db: Annotated[AsyncSession, Depends(get_pg_session)], input_order: OrderSchema
) -> Any:
    order_service = get_order_service(db)
    input_order.user_id = request.state.user_id
    order = await order_service.create_order(input_order)
    return order.id


@router.post("/refund_order")
async def refund_order(db: Annotated[AsyncSession, Depends(get_pg_session)], order_id: str) -> bool:
    order_service = get_order_service(db)
    status = await order_service.refund_order(order_id)
    return cast(bool, status)
