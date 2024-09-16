from __future__ import annotations

from typing import Annotated, Any

from uuid import UUID  # noqa: TCH003

from fastapi import APIRouter, Depends, Request
from starlette import status

from schemas.entity import ProductSchema
from services import EntityService, get_entity_service

router = APIRouter()


@router.post(
    "/create_product", status_code=status.HTTP_201_CREATED, summary="Create product", description="Create product"
)
async def create_product(
    service: Annotated[EntityService, Depends(get_entity_service)], input_product: ProductSchema
) -> Any:
    return await service.create_product(input_product)


@router.post(
    "/create_user_product",
    status_code=status.HTTP_201_CREATED,
    summary="Create user product",
    description="Create user product",
)
async def create_user_product(
    request: Request, service: Annotated[EntityService, Depends(get_entity_service)], product_id: UUID
) -> Any:
    user_id = request.state.user_id
    return await service.create_user_product(user_id, product_id)
