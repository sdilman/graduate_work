from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class DefaultSettings(BaseSettings):
    """Class to store default project settings."""

    model_config = SettingsConfigDict(env_file="../.env", env_file_encoding="utf-8", extra="ignore")


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


class Settings:
    app: AppSettings = AppSettings()
    api: ApiSettings = ApiSettings()


settings = Settings()
