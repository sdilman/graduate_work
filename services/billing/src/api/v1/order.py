from __future__ import annotations

from fastapi import APIRouter, Cookie, Depends
from schemas.authentication import UserAuthError, UserAuthInfoResponce  # noqa: TCH002
from schemas.cookie import AccessTokenCookie

from services.authentication import AuthService, get_auth_service

router = APIRouter()


@router.get("/create")
async def create_order(
    input_token: str = Cookie(alias=AccessTokenCookie.name),
    auth_service: AuthService = Depends(get_auth_service),  # noqa: B008
) -> UserAuthInfoResponce | UserAuthError:
    return await auth_service.authenticate_user(input_token)
