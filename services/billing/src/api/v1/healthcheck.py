from __future__ import annotations

from fastapi import APIRouter

router = APIRouter()


@router.get("/check")
async def health_check() -> dict[str, str]:
    return {"status": "ok"}
