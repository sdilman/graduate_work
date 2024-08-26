from __future__ import annotations

from fastapi import APIRouter, Request

router = APIRouter()


@router.get("/check")
async def health_check(request: Request) -> dict[str, str]:  # noqa: ARG001
    return {"status": "ok"}
