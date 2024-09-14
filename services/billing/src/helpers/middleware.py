from __future__ import annotations

from typing import Any, Callable

from async_fastapi_jwt_auth import AuthJWT
from async_fastapi_jwt_auth.exceptions import AuthJWTException
from fastapi import FastAPI, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from core.logger import get_logger
from core.settings import settings as config
from helpers.exempt_endpoints import get_exempt_endpoints

logger = get_logger(__name__)


class AuthService:
    """Handle authentication-related operations."""

    def __init__(self, authjwt: AuthJWT):
        self.authjwt = authjwt

    async def authenticate(self, request: Request) -> Any:
        self.authjwt._request = request  # noqa: SLF001
        await self.authjwt.jwt_required()
        return await self.authjwt.get_raw_jwt()


class PermissionChecker:
    """Handle permission checking for the user."""

    def __init__(self, exempt_endpoints_provider: Callable[[], list[str]]):
        self.exempt_endpoints_provider = exempt_endpoints_provider

    def is_exempt(self, path: str) -> bool:
        exempt_endpoints = self.exempt_endpoints_provider()
        return path in exempt_endpoints

    @staticmethod
    def has_permission(user_permissions: list[str], path: str) -> bool:
        return any(path.startswith(permission) for permission in user_permissions)


class PermissionMiddleware(BaseHTTPMiddleware):
    """Checks user permissions before processing a request."""

    def __init__(self, app: FastAPI, auth_service: AuthService, permission_checker: PermissionChecker):
        super().__init__(app)
        self.auth_service = auth_service
        self.permission_checker = permission_checker
        logger.info("Permission middleware initialized")

    async def dispatch(self, request: Request, call_next: Callable[..., Any]) -> JSONResponse:
        path = request.url.path.split(config.api.version)[-1]

        logger.info("Checking permissions for path: %s", path)

        if not self.permission_checker.is_exempt(path):
            try:
                current_user = await self.auth_service.authenticate(request)
                logger.debug("Current user: %s", current_user)

                if not current_user:
                    return JSONResponse(
                        status_code=status.HTTP_401_UNAUTHORIZED, content={"detail": "Invalid credentials."}
                    )

                current_user_permissions = current_user.get("permissions", [])
                if not self.permission_checker.has_permission(current_user_permissions, path):
                    return JSONResponse(
                        status_code=status.HTTP_403_FORBIDDEN, content={"detail": "Insufficient rights."}
                    )

                request.state.user_id = current_user.get("user_id")

            except AuthJWTException as e:
                logger.exception("AuthJWTException: JWT token Encoding Error", exc_info=e)
                return JSONResponse(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    content={"detail": "Session expired. Login again."},
                )

        return await call_next(request)

    async def __call__(self, scope: Any, receive: Any, send: Any) -> None:
        await super().__call__(scope, receive, send)


# Dependency Injection setup
def setup_middleware(app: FastAPI) -> None:
    auth_service = AuthService(AuthJWT())
    permission_checker = PermissionChecker(get_exempt_endpoints)
    app.add_middleware(PermissionMiddleware, auth_service=auth_service, permission_checker=permission_checker)
