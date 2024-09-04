from fastapi import APIRouter

from api.v1 import auxiliary, healthcheck, order

router = APIRouter()
router.include_router(healthcheck.router, prefix="/healthcheck", tags=["healthcheck"])
router.include_router(order.router, prefix="/order", tags=["order"])
router.include_router(auxiliary.router, prefix="/auxiliary", tags=["auxiliary"])
