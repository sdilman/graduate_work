from fastapi import APIRouter

from api.v1 import auxiliary, healthcheck, order, payment, product

router = APIRouter()
router.include_router(healthcheck.router)
router.include_router(order.router)
router.include_router(auxiliary.router)
router.include_router(payment.router)
router.include_router(product.router)
