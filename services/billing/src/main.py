import uvicorn

from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

from api import router as router_api
from core.config import settings
from core.exceptions import register_exception_handlers
from core.logger import setup_logging

# TODO: from helpers.lifespan import lifespan
from helpers.middleware import BaseMiddleware

setup_logging()


app = FastAPI(
    root_path=settings.app.root_path,
    title=settings.app.name,
    default_response_class=ORJSONResponse,
    docs_url=settings.api.docs_url,
    openapi_url=settings.api.openapi_url,
    # TODO: lifespan=lifespan,
)

app.add_middleware(BaseMiddleware)
register_exception_handlers(app=app)
app.include_router(router_api, prefix="/api")

if __name__ == "__main__":
    uvicorn.run("main:app", host=settings.app.host, port=settings.app.port)
