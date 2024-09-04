"""
Module to store all test settings in one place.
"""

import os

from dotenv import find_dotenv, load_dotenv
from pydantic import ConfigDict, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv(find_dotenv())

current_dir = os.path.dirname(os.path.abspath(__file__))


class DefaultSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


class TestBaseSettings(DefaultSettings):
    model_config = ConfigDict(extra="ignore")
    # Postgres
    pg_db: str = Field("", env="PG_DB")
    pg_user: str = Field("", env="PG_USER")
    pg_password: str = Field("", env="PG_PASSWORD")
    pg_host: str = Field("127.0.0.1", env="PG_HOST")
    pg_port: int = Field(5433, env="PG_PORT")
    # Redis
    redis_host: str = Field("127.0.0.1", env="REDIS_HOST")
    redis_port: int = Field(6379, env="REDIS_PORT")

    service_host: str = Field("0.0.0.0", env="API_HOST")
    service_port: int = Field(8000, env="API_PORT")
    # JWT token
    jwt_secret_key: str = Field(env="JWT_SECRET_KEY")
    jwt_algorithm: str = Field(env="JWT_ALGORITHM")
    jwt_at_expire_minutes: int = Field(env="JWT_AT_EXPIRE_MINUTES")

    current_folder: str = Field(current_dir)


test_base_settings = TestBaseSettings()
