from __future__ import annotations

from typing import Annotated, Any

from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from db.postgres import get_pg_session
from services.product_service import get_product_service

router = APIRouter()


@router.post("/cancel_auto_renewal")
async def cancel_auto_renewal(
    request: Request, db: Annotated[AsyncSession, Depends(get_pg_session)], product_id: str
) -> Any:
    product_service = get_product_service(db)
    user_id = request.state.user_id
    return await product_service.disable_renewal(user_id, product_id)
