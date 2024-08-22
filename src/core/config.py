from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class DefaultSettings(BaseSettings):
    """
    Class to store default project settings.
    """

    model_config = SettingsConfigDict(env_file="../.env", env_file_encoding="utf-8", extra="ignore")
    # TODO: we don't have .env in PROD - make sure all entries get load from env vars


class ProjectSettings(DefaultSettings):
    app_name: str = Field(...)
    app_host: str = Field(...)
    app_port: int = Field(...)
    app_root_path: str = Field(...)


class ApiSettings(DefaultSettings):
    docs_url: str = Field(...),
    openapi_url: str = Field(...),
    version: str = Field(...),  # "v1"  


class Settings():
    project_settings = ProjectSettings()
    api_settings = ApiSettings()


settings = Settings()
