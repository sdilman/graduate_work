from __future__ import annotations

from typing import Annotated, Any

from fastapi import APIRouter, Depends, Request
from starlette import status

from schemas.entity import OrderSchema
from services import OrderService, get_order_service

router = APIRouter()


@router.post(
    "/create_order",
    status_code=status.HTTP_201_CREATED,
    summary="Create a new order",
    description="""
        The server validates the provided **idempotency key** by checking it against the cache to prevent duplicate operations.
        If the key is already present in the cache, the request is rejected with a **409 Conflict** error, ensuring that the same
        operation is not processed multiple times.
    """,
)
async def create_order(
    request: Request, schema_in: OrderSchema, service: Annotated[OrderService, Depends(get_order_service)]
) -> Any:
    schema_in.user_id = request.state.user_id
    order = await service.create_order(schema_in)
    return order.id
