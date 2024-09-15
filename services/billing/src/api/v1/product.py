from __future__ import annotations

from typing import Annotated, Any

from fastapi import APIRouter, Depends, Request
from starlette import status

from services import ProductService, get_product_service

router = APIRouter()


@router.post(
    "/cancel_auto_renewal",
    status_code=status.HTTP_200_OK,
    summary="Disable auto renewal for a product",
    description="Disable auto renewal for a product",
)
async def cancel_auto_renewal(
    request: Request, service: Annotated[ProductService, Depends(get_product_service)], product_id: str
) -> Any:
    user_id = request.state.user_id
    return await service.disable_renewal(user_id, product_id)
