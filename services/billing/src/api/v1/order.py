from __future__ import annotations

from typing import Annotated, Any

from fastapi import APIRouter, Depends, Request

from schemas.entity import OrderSchema
from services import OrderService, get_order_service

router = APIRouter()


@router.post("/create_order")
async def create_order(
    request: Request, schema_in: OrderSchema, service: Annotated[OrderService, Depends(get_order_service)]
) -> Any:
    schema_in.user_id = request.state.user_id
    order = await service.create_order(schema_in)
    return order.id
