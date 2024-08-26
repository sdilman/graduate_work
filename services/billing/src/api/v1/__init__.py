from api.v1 import healthcheck
from fastapi import APIRouter

router = APIRouter()
router.include_router(healthcheck.router, prefix="/healthcheck", tags=["healthcheck"])
