from dataclasses import dataclass

from core.settings import settings


@dataclass(frozen=True)
class AccessTokenCookie:
    value: str
    name: str = settings.auth.access_name


@dataclass(frozen=True)
class RefreshTokenCookie:
    value: str
    name: str = settings.auth.refresh_name
