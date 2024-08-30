from __future__ import annotations

from dataclasses import asdict
from functools import lru_cache

import httpx

from core.config import settings
from schemas.authentication import UserAuthError, UserAuthInfoRequest, UserAuthInfoResponce


class AuthService:
    async def authenticate_user(self, input_token: str) -> UserAuthInfoResponce | UserAuthError:
        async with httpx.AsyncClient() as client:
            url = settings.auth.url_user
            payload = UserAuthInfoRequest(input_token=input_token)
            response = await client.post(url, json=asdict(payload))
            if response.status_code == 200:
                return UserAuthInfoResponce(**response.json())
            return UserAuthError(message=response.status_code)


@lru_cache
def get_auth_service():
    return AuthService()
