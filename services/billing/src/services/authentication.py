from functools import lru_cache

import httpx

from dataclasses import asdict

from core.config import settings

from schemas.authentication import (
    UserAuthInfoRequest, 
    UserAuthInfoResponce, 
    UserAuthError
)


class AuthService:
    async def authenticate_user(self, input_token: str) -> UserAuthInfoResponce | UserAuthError:
        async with httpx.AsyncClient() as client:
            url = settings.auth.url_user
            payload = UserAuthInfoRequest(input_token=input_token)
            response = await client.post(url, json=asdict(payload))
            if response.status_code == 200:
                return UserAuthInfoResponce(**response.json())
            else:
                return UserAuthError(message=response.status_code)


@lru_cache()
def get_auth_service():
    return AuthService()

