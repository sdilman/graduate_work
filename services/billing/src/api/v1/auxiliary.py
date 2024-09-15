from __future__ import annotations

from typing import Annotated, Any

from uuid import UUID  # noqa: TCH003

from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from db.postgres import get_pg_session
from schemas.entity import ProductSchema
from services.entity import EntityService, get_entity_service

router = APIRouter()


@router.post("/create_product")
async def create_product(
    entity_service: Annotated[EntityService, Depends(get_entity_service)],
    db: Annotated[AsyncSession, Depends(get_pg_session)],
    input_product: ProductSchema,
) -> Any:
    return await entity_service.create_product(db, input_product)


@router.post("/create_user_product")
async def create_user_product(
    request: Request,
    entity_service: Annotated[EntityService, Depends(get_entity_service)],
    db: Annotated[AsyncSession, Depends(get_pg_session)],
    product_id: UUID,
) -> Any:
    user_id = request.state.user_id
    return await entity_service.create_user_product(db, user_id, product_id)
