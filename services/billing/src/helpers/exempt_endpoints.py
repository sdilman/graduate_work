from __future__ import annotations

from pydantic import BaseModel

from core.settings import settings as config


class ExemptEndpoints(BaseModel):
    """List of exempt endpoints."""

    healthcheck: str = "/check"
    docs: str = config.api.docs_url.split(config.api.version)[-1]
    openai: str = config.api.openapi_url.split(config.api.version)[-1]
    results_callback: str = config.api.results_callback_url.split(config.api.version)[-1]


def get_exempt_endpoints() -> list[str]:
    """Get list of exempt endpoints"""
    exempt_endpoints = ExemptEndpoints().model_dump().values()
    return list(exempt_endpoints)
