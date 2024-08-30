import os

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class DefaultSettings(BaseSettings):
    """Class to store default project settings."""

    env_file: str = "../.env"

    if os.getenv("IS_TEST_FUNCTIONAL"):
        env_file = "../tests/functional/.env"

    model_config = SettingsConfigDict(env_file=env_file, env_file_encoding="utf-8", extra="ignore")


class AppSettings(DefaultSettings):
    name: str = Field(...)
    host: str = Field(...)
    port: int = Field(...)
    root_path: str = Field(...)

    model_config = SettingsConfigDict(env_prefix="APP_")


class ApiSettings(DefaultSettings):
    docs_url: str = Field(...)
    openapi_url: str = Field(...)
    version: str = Field(...)

    model_config = SettingsConfigDict(env_prefix="API_")


class PGSettings(DefaultSettings):
    db: str = Field(...)
    user: str = Field(...)
    password: str = Field(...)
    host: str = Field(...)
    port: int = Field(...)
    dsn: str = Field(...)
    dsn_local: str = Field(...)
    async_schema: str = Field(...)

    model_config = SettingsConfigDict(env_prefix="PG_")


class Auth(DefaultSettings):
    access_name: str = Field(...)
    refresh_name: str = Field(...)
    url_user: str = Field(...)

    model_config = SettingsConfigDict(env_prefix="AUTH_")


class Settings:
    debug: bool = False
    app: AppSettings = AppSettings()
    api: ApiSettings = ApiSettings()
    pg: PGSettings = PGSettings()
    auth: Auth = Auth()


settings = Settings()
