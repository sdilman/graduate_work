from typing import Any, Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.types import ASGIApp, Receive, Scope, Send

from core.logger import get_logger
from core.settings import settings as config

logger = get_logger(__name__)


class BaseMiddleware(BaseHTTPMiddleware):
    """
    Base class middleware for any work before processing a request.
    """

    def __init__(self, app: ASGIApp):
        super().__init__(app)

        logger.info("Base middleware initialized")

    async def dispatch(self, request: Request, call_next: Callable[..., Any]) -> JSONResponse:
        path = request.url.path.split(config.api.version)[-1]

        logger.info("Base middleware dispatching for path %s", path)

        return await call_next(request)

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        logger.info(msg="Base middleware called")

        await super().__call__(scope, receive, send)
