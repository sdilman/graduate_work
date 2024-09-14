import uvicorn

from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

from api import setup_routers
from core.exceptions import register_exception_handlers
from core.logger import setup_logging
from core.settings import settings
from helpers.lifespan import lifespan
from helpers.middleware import setup_middleware

setup_logging()

app = FastAPI(
    root_path=settings.app.root_path,
    title=settings.app.name,
    default_response_class=ORJSONResponse,
    docs_url=settings.api.docs_url,
    openapi_url=settings.api.openapi_url,
    lifespan=lifespan,
)

setup_middleware(app=app)
register_exception_handlers(app=app)
setup_routers(app=app)

if __name__ == "__main__":
    uvicorn.run("main:app", host=settings.app.host, port=settings.app.port)
