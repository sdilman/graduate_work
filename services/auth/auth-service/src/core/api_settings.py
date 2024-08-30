from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class DefaultSettings(BaseSettings):
    """
    Class to store default fastapi project settings.
    """

    model_config = SettingsConfigDict(env_file="../.env", env_file_encoding="utf-8", extra="ignore")


class SuperUserSettings(DefaultSettings):
    hashed_password: str = Field(default="securepassword245")
    email: str = Field(default="admin@example.com")
    is_active: bool = Field(default=True)
    is_superuser: bool = Field(default=True)
    is_verified: bool = Field(default=True)

    model_config = SettingsConfigDict(env_prefix="SUPERUSER_")


class Settings(DefaultSettings):
    """
    Class to store fastapi project settings.
    """

    project_name: str = Field("Auth API", env="API_PROJECT_NAME")
    service_name: str = Field("auth-service", env="API_SERVICE_NAME")
    project_root: str = Field(default="app")
    api_port: str = Field("api_port", env="API_PORT")
    # Redis
    redis_host: str = Field("127.0.0.1", env="REDIS_HOST")
    redis_port: int = Field(6380, env="REDIS_PORT")
    # Postgres
    pg_db: str = Field("", env="PG_DB")
    pg_user: str = Field("", env="PG_USER")
    pg_password: str = Field("", env="PG_PASSWORD")
    pg_host: str = Field("127.0.0.1", env="PG_HOST")
    pg_port: int = Field(5433, env="PG_PORT")
    pg_dsn: str = Field("", env="PG_DSN")
    pg_dsn_local: str = Field("", env="PG_DSN_LOCAL")
    # Logging
    log_format: str = Field("%(asctime)s - %(name)s - %(levelname)s - %(message)s", env="API_LOG_FORMAT")
    log_default_handlers: list = Field(["console"], env="API_LOG_DEFAULT_HANDLERS")
    console_log_lvl: str = Field("DEBUG", env="API_CONSOLE_LOG_LVL")
    loggers_handlers_log_lvl: str = Field("INFO", env="API_LOGGERS_HANDLERS_LOG")
    unicorn_error_log_lvl: str = Field("INFO", env="API_UNICORN_ERROR_LOG_LVL")
    unicorn_access_log_lvl: str = Field("INFO", env="API_UNICORN_ACCESS_LOG_LVL")
    root_log_lvl: str = Field("INFO", env="API_ROOT_LOG_LVL")
    # JWT token settings
    jwt_secret_key: str = Field(env="JWT_SECRET_KEY")
    jwt_algorithm: str = Field("HS256", env="JWT_ALGORITHM")
    jwt_at_expire_minutes: int = Field(30, env="JWT_ACCESS_TOKEN_EXPIRE_MINUTES")
    jwt_rt_expire_minutes: int = Field(1440, env="JWT_REFRESH_TOKEN_EXPIRE_MINUTES")
    # External login settings (Yandex)
    yauth_secret_key: str = Field(env="YAUTH_SECRET_KEY")
    yauth_client_id: str = Field(env="YAUTH_CLIENT_ID")
    yauth_token_url: str = Field(env="YAUTH_TOKEN_URL")
    yauth_user_info_url: str = Field(env="YAUTH_USER_INFO_URL")
    yauth_authorize_url: str = Field(env="YAUTH_AUTHORIZE_URL")
    yauth_authenticate_redirect_uri: str = Field(env="YAUTH_AUTHENTICATE_REDIRECT_URI")
    yauth_authenticate_state: str = Field(env="YAUTH_AUTHENTICATE_STATE")
    # External login settings (Google)
    gauth_secret_key: str = Field(env="GAUTH_SECRET_KEY")
    gauth_client_id: str = Field(env="GAUTH_CLIENT_ID")
    # External login settings (VK)
    vauth_secret_key: str = Field(env="VAUTH_SECRET_KEY")
    vauth_client_id: str = Field(env="VAUTH_CLIENT_ID")
    # Tracer
    jaeger_enable_tracer: bool = Field(default=False, env="JAEGER_ENABLE_TRACER")
    jaeger_host: str = Field(default="jaeger", env="JAEGER_HOST")
    jaeger_port: int = Field(default=6831, env="JAEGER_PORT")
    # Sentry
    sentry_dsn: str = Field(default="", env="SENTRY_DSN")
    sentry_traces_sample_rate: float = Field(default=1, env="SENTRY_TRACES_SAMPLE_RATE")
    sentry_profiles_sample_rate: float = Field(default=1, env="SENTRY_PROFILES_SAMPLE_RATE")
    # Rate limit
    register_rate_limit_times: int = Field(default=3, env="REGISTER_RATE_LIMIT_TIMES")
    register_rate_limit_seconds: int = Field(default=60 * 5, env="REGISTER_RATE_LIMIT_SECONDS")

    su: SuperUserSettings = SuperUserSettings()


settings = Settings()
