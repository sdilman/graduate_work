from api.v1 import router as router_v1
from fastapi import APIRouter

router = APIRouter()
router.include_router(router_v1, prefix="/v1", tags=["v1"])
