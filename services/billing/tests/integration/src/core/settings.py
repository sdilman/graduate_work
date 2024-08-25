from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class DefaultSettings(BaseSettings):
    """Class to store default project settings."""

    model_config = SettingsConfigDict(env_file="../.env", env_file_encoding="utf-8", extra="ignore")


class AppSettings(DefaultSettings):
    base_url: str = "http://app:8075"
    health_check_path: str = "/billing/api/v1/healthcheck/check"


class Settings:
    app: AppSettings = AppSettings()


settings = Settings()
