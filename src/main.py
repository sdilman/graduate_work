import uvicorn
from src.api import router as router_api
from src.core import exceptions
from src.core.config import settings
from src.core.logger import setup_logging
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
# from helpers.lifespan import lifespan  # TODO:
from src.helpers.middleware import BaseMiddleware


setup_logging()


app = FastAPI(
    root_path=settings.project_settings.app_root_path,
    title=settings.project_settings.app_name,
    default_response_class=ORJSONResponse,
    docs_url="/api/" + settings.api_settings.version + "/" + settings.api_settings.docs_url,
    openapi_url="/api/" + settings.api_settings.version + "/" + settings.api_settings.openapi_url,
    # lifespan=lifespan,  # TODO:
)

app.add_middleware(BaseMiddleware)
exceptions.register_exception_handlers(app=app)
app.include_router(router_api, prefix="/api")

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.app_host,
        port=settings.app_port,
    )
