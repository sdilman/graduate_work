from __future__ import annotations

import hashlib
import time

from pathlib import Path

from async_fastapi_jwt_auth import AuthJWT
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
    base_url: str = "http://billing_app_backend:8075"
    health_check_path: str = "/billing/api/v1/check"

    model_config = SettingsConfigDict(env_prefix="APP_")


class ApiSettings(DefaultSettings):
    docs_url: str = Field(...)
    openapi_url: str = Field(...)
    version: str = Field(...)
    results_callback_url: str = Field(...)

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
    max_tries: int = Field(...)
    max_time: int = Field(...)

    model_config = SettingsConfigDict(env_prefix="BACKOFF_")


class JWTSettings(DefaultSettings):
    """Class to store JWT project settings."""

    permissions_enabled: bool = Field(default=False, description="Enable permissions check in JWT")
    authjwt_algorithm: str = Field(...)
    authjwt_secret_key: str = Field(...)
    authjwt_token_location: set[str] = {"cookies"}
    authjwt_cookie_csrf_protect: bool = False
    authjwt_access_token_expires: int = Field(...)
    authjwt_access_cookie_key: str = Field(...)
    authjwt_refresh_cookie_key: str = Field(...)

    model_config = SettingsConfigDict(env_prefix="JWT_")


class KafkaSettings(DefaultSettings):
    """Class to store Kafka project settings."""

    topic_name: str = Field(
        default="payment_processing_topic", description="backward compatibility with previous version of billing"
    )
    enable_idempotence: bool = True
    acks: str = "all"
    bootstrap_servers: str = Field(...)
    group_id: str = Field(...)
    retry_backoff_ms: int = Field(...)
    config_path: Path = Path(__file__).resolve().parent.parent / "broker" / "topics" / "config.json"

    model_config = SettingsConfigDict(env_prefix="KAFKA_")

    def generate_transaction_id(self) -> str:
        """Generate unique transaction id."""
        unique_string = f"{self.bootstrap_servers}{time.time()}"
        return hashlib.sha256(unique_string.encode("utf-8")).hexdigest()


class RedisSettings(DefaultSettings):
    host: str = Field(...)
    port: int = Field(...)
    dsn: str = Field(...)
    backoff_max_time: int = Field(...)
    backoff_max_tries: int = Field(...)
    record_expiration_time: int = Field(...)
    prefix: str = "idempotency_key:"

    model_config = SettingsConfigDict(env_prefix="REDIS_")


class PaymentSettings(DefaultSettings):
    account_id: str = Field(...)
    secret_key: str = Field(...)
    return_url: str = Field(...)

    model_config = SettingsConfigDict(env_prefix="YOOKASSA_")


class Settings:
    debug: bool = False
    app: AppSettings = AppSettings()
    api: ApiSettings = ApiSettings()
    pg: PGSettings = PGSettings()
    auth: Auth = Auth()
    redis: RedisSettings = RedisSettings()
    backoff: BackoffSettings = BackoffSettings()
    payment: PaymentSettings = PaymentSettings()
    jwt: JWTSettings = JWTSettings()
    kafka: KafkaSettings = KafkaSettings()


settings = Settings()


def get_settings() -> Settings:
    """Provide settings."""
    return settings


@AuthJWT.load_config
def get_config() -> JWTSettings:
    return JWTSettings()
