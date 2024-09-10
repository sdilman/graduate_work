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
    create_product_path: str = "/billing/api/v1/create_product"
    create_order_path: str = "/billing/api/v1/create_order"
    create_payment_link_path: str = "/billing/api/v1/payment_create/{order_id}"


class AuthSettings(DefaultSettings):
    base_url: str = "http://auth_app_backend:8001"
    health_check_path: str = "/auth/api/v1/check"
    register_user_path: str = "/auth/api/v1/register"
    login_user_path: str = "/auth/api/v1/login"
    access_name: str = "auth-app-access-key"


class BackoffSettings(DefaultSettings):
    max_tries: int = Field(default=300)
    max_time: int = Field(default=60)

    model_config = SettingsConfigDict(env_prefix="BACKOFF_")


class Settings:
    app: AppSettings = AppSettings()
    auth: AuthSettings = AuthSettings()
    backoff: BackoffSettings = BackoffSettings()


settings = Settings()
