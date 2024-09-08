from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Cookie, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from db.postgres import get_pg_session
from schemas.cookie import AccessTokenCookie
from services.authentication import AuthService, get_auth_service
from services.entity import EntityService, get_entity_service
from services.payment import PaymentService, get_payment_service
from services.redis import RedisService, get_redis_service

router = APIRouter()


@router.post("/payment_create/{order_id}")
async def create_payment_link(
    order_id: str,
    request: Request,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
    entity_service: Annotated[EntityService, Depends(get_entity_service)],
    payment: Annotated[PaymentService, Depends(get_payment_service)],
    redis: Annotated[RedisService, Depends(get_redis_service)],
    db: Annotated[AsyncSession, Depends(get_pg_session)],
    input_token: str = Cookie(alias=AccessTokenCookie.name),
) -> str:
    user_external = await auth_service.authenticate_user(input_token)
    # TODO: проверка ID юзера
    order = await entity_service.get_order(db, order_id)
    if order is None:
        raise HTTPException(status_code=500, detail=f"Order with id={order_id} not found")

    try:
        cache_key = await redis.get_cache_key(order_id=order_id)
        cached_value: str | None = await redis.get_value_by_key(key=cache_key)
        if cached_value:
            await redis.refresh_payment_link(key=cache_key)
            return cached_value

        link: str = await payment.create_payment_link(
            base_url=request.base_url, amount=order.total_amount, currency=order.currency.value.upper(), description=""
        )
        await redis.save_payment_link(order_id=order_id, payment_link=link)
    except Exception as e:
        raise HTTPException(status_code=500) from e
    else:
        return link


@router.get("/payment_create_callback")
async def payment_callback() -> str:
    return "callback OK"
    # TODO:
