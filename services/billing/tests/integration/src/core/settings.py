from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv())


class DefaultSettings(BaseSettings):
    """Class to store default project settings."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


class AppSettings(DefaultSettings):
    base_url: str = "http://app:8075"
    health_check_path: str = "/billing/api/v1/check"


class BackoffSettings(DefaultSettings):
    max_tries: int = Field(default=300)
    max_time: int = Field(default=60)

    model_config = SettingsConfigDict(env_prefix="BACKOFF_")


class Settings:
    app: AppSettings = AppSettings()
    backoff: BackoffSettings = BackoffSettings()


settings = Settings()
