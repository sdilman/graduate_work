from typing import Any, Callable

from src.core.config import settings as config
from src.core.logger import get_logger
from fastapi import FastAPI, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse


logger = get_logger(__name__)


class BaseMiddleware(BaseHTTPMiddleware):
    """
    Base class middleware for any work before processing a request.
    """

    def __init__(self, app: FastAPI):
        super().__init__(app)
        
        logger.info("Base middleware initialized")

    async def dispatch(self, request: Request, call_next: Callable[..., Any]) -> JSONResponse:
        path = request.url.path.split(config.api_settings.version)[-1]

        logger.info(f"Base middleware dispatching for path: {path}")

        return await call_next(request)

    async def __call__(self, scope: Any, receive: Any, send: Any) -> None:
        logger.info(f"Base middleware called")

        await super().__call__(scope, receive, send)
