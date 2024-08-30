from __future__ import annotations

from typing import Dict

from fastapi import APIRouter, Request, Cookie, Depends

from schemas.cookie import AccessTokenCookie, RefreshTokenCookie
from schemas.authentication import UserAuthInfoResponce, UserAuthError
from services.authentication import AuthService, get_auth_service

router = APIRouter()


@router.get("/create")
async def create_order(
    input_token: str = Cookie(alias=AccessTokenCookie.name),
    auth_service: AuthService = Depends(get_auth_service)
) -> UserAuthInfoResponce | UserAuthError:
    response = await auth_service.authenticate_user(input_token)
    return response