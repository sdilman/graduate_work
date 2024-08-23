from fastapi import APIRouter

from src.api.v1 import healthcheck


router = APIRouter()
router.include_router(healthcheck.router, prefix="/healthcheck", tags=["healthcheck"])