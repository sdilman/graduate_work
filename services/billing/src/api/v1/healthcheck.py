from __future__ import annotations

from typing import Dict

from fastapi import APIRouter, Request

router = APIRouter()


@router.get("/check")
async def health_check(request: Request) -> Dict[str, str]:
    return {"status": "ok"}
