from dotenv import find_dotenv, load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv(find_dotenv())


class DefaultSettings(BaseSettings):
    """Class to store default project settings."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


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
    dsn_pg: str = Field(...)

    model_config = SettingsConfigDict(env_prefix="POSTGRES_")


class Auth(DefaultSettings):
    access_name: str = Field(...)
    refresh_name: str = Field(...)
    url_user: str = Field(...)

    model_config = SettingsConfigDict(env_prefix="AUTH_")


class BackoffSettings(DefaultSettings):
    max_tries: int = Field(default=10)
    max_time: int = Field(default=60)

    model_config = SettingsConfigDict(env_prefix="BACKOFF_")


class RedisSettings(DefaultSettings):
    host: str = Field("127.0.0.1")
    port: int = Field(6380)
    dsn: str = Field("")

    model_config = SettingsConfigDict(env_prefix="REDIS_")


class Settings:
    debug: bool = False
    app: AppSettings = AppSettings()
    api: ApiSettings = ApiSettings()
    pg: PGSettings = PGSettings()
    auth: Auth = Auth()
    redis: RedisSettings = RedisSettings()
    backoff: BackoffSettings = BackoffSettings()


settings = Settings()
