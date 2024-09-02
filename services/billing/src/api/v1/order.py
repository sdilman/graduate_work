from __future__ import annotations

from typing import Annotated, Any

from db.postgres import get_pg_session
from fastapi import APIRouter, Cookie, Depends
from schemas.cookie import AccessTokenCookie
from schemas.entity import OrderSchema
from sqlalchemy.ext.asyncio import AsyncSession

from services.authentication import AuthService, get_auth_service
from services.entity import EntityService, get_entity_service

router = APIRouter()


@router.post("/create_order")
async def create_order(
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
    entity_service: Annotated[EntityService, Depends(get_entity_service)],
    db: Annotated[AsyncSession, Depends(get_pg_session)],
    input_order: OrderSchema,
    input_token: str = Cookie(alias=AccessTokenCookie.name),
) -> Any:
    user_external = await auth_service.authenticate_user(input_token)
    # TODO: проверка ID юзера - должен совпасть sso_id
    return await entity_service.create_order(db, input_order)
