from __future__ import annotations

from typing import Annotated, Any

from fastapi import APIRouter, Depends
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
