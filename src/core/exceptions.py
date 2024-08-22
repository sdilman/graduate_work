from typing import Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import ORJSONResponse, Response
from starlette import status
from starlette.responses import JSONResponse

from src.core.logger import get_logger

logger = get_logger(__name__)


class BaseError(Exception):
    """Base class for errors.

    Attributes:
        status_code (int): The HTTP status code associated with the error.
        body (Any): The response body associated with the error.
        errors (Tuple[Exception, ...]): A tuple of related exceptions.
    """

    def __init__(
        self,
        message: str,
        status_code: int,
        body: Any,
        errors: tuple[Exception, ...] | None = None,
    ):
        """
        Initialize the ServiceError.

        Args:
            message (str): The error message.
            status_code (int): The HTTP status code associated with the error.
            body (Any): The response body associated with the error.
            errors (Optional[Tuple[Exception, ...]]): A tuple of related exceptions.
        """
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.body = body
        self.errors = errors if errors is not None else ()


class BadRequestError(BaseError):
    """Exception representing a 400 status code."""

    pass


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> Response:
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=jsonable_encoder({"detail": exc.errors(), "body": exc.body}),
    )


async def http_exception_handler(request: Request, exc: HTTPException) -> Response:
    logger.error(f"HTTPException: {exc}")
    return ORJSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )


async def bad_request_exception_handler(request: Request, exc: BadRequestError) -> Response:
    logger.error(f"BadRequestError: {exc}")
    return ORJSONResponse(
        status_code=exc.status_code,
        content={
            "message": exc.message,
            "body": exc.body,
            "errors": [str(error) for error in exc.errors],
        },
    )


async def generic_exception_handler(request: Request, exc: Exception) -> Response:
    logger.error(f"Unhandled exception: {exc}")
    return ORJSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"message": "Internal Server Error"},
    )


def register_exception_handlers(app: FastAPI) -> None:
    """Register exception handlers for the application.

    Args:
        app (FastAPI): The FastAPI application.
    """
    app.add_exception_handler(RequestValidationError, validation_exception_handler)  # type: ignore
    app.add_exception_handler(HTTPException, http_exception_handler)  # type: ignore
    app.add_exception_handler(BadRequestError, bad_request_exception_handler)  # type: ignore
    app.add_exception_handler(Exception, generic_exception_handler)
