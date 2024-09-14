from __future__ import annotations

from typing import Annotated, Any

from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from db.postgres import get_pg_session
from schemas.entity import OrderSchema
from services.entity import EntityService, get_entity_service

router = APIRouter()


@router.post("/create_order")
async def create_order(
    request: Request,
    entity_service: Annotated[EntityService, Depends(get_entity_service)],
    db: Annotated[AsyncSession, Depends(get_pg_session)],
    input_order: OrderSchema,
) -> Any:
    input_order.user_id = request.state.user_id
    return await entity_service.create_order(db, input_order)
