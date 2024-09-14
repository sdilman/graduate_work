from fastapi import APIRouter, FastAPI

from api.v1 import router as v1_router

api_router = APIRouter(prefix="/api")
api_router.include_router(v1_router, prefix="/v1", tags=["v1"])


def setup_routers(app: FastAPI) -> None:
    root_router = APIRouter()
    root_router.include_router(api_router)
    app.include_router(root_router)
