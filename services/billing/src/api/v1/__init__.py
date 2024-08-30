from api.v1 import healthcheck, order
from fastapi import APIRouter

router = APIRouter()
router.include_router(healthcheck.router, prefix="/healthcheck", tags=["healthcheck"])
router.include_router(order.router, prefix="/order", tags=["order"])
