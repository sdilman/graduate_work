from __future__ import annotations

from typing import Annotated, Any

from fastapi import APIRouter, Depends, Request

from schemas.entity import OrderSchema
from services.order_service import OrderService, get_order_service

router = APIRouter()


@router.post("/create_order")
async def create_order(
    request: Request, order_service: Annotated[OrderService, Depends(get_order_service)], input_order: OrderSchema
) -> Any:
    input_order.user_id = request.state.user_id
    return await order_service.create_order(input_order)
