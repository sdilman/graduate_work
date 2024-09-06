from fastapi import APIRouter

from api.v1 import auxiliary, healthcheck, order

router = APIRouter()
router.include_router(healthcheck.router, prefix="/v1", tags=["v1"])
router.include_router(order.router, prefix="/v1", tags=["v1"])
router.include_router(auxiliary.router, prefix="/v1", tags=["v1"])
