from __future__ import annotations

from typing import Annotated, Any, cast

from fastapi import APIRouter, Depends, Request

from schemas.entity import OrderSchema
from services import OrderService, get_order_service

router = APIRouter()


@router.post("/create_order")
async def create_order(
    request: Request, order_service: Annotated[OrderService, Depends(get_order_service)], input_order: OrderSchema
) -> Any:
    input_order.user_id = request.state.user_id
    order = await order_service.create_order(input_order)
    return order.id


@router.post("/refund_order")
async def refund_order(order_service: Annotated[OrderService, Depends(get_order_service)], order_id: str) -> bool:
    status = await order_service.refund_order(order_id)
    return cast(bool, status)
