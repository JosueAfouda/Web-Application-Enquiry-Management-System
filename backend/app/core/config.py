from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_env: str = Field(default="local", alias="APP_ENV")
    app_name: str = Field(default="ems", alias="APP_NAME")
    app_version: str = Field(default="0.1.0", alias="APP_VERSION")
    secret_key: str = Field(default="change-me", alias="SECRET_KEY")
    jwt_algorithm: str = Field(default="HS256", alias="JWT_ALGORITHM")
    access_token_expire_minutes: int = Field(
        default=60,
        alias="ACCESS_TOKEN_EXPIRE_MINUTES",
    )
    refresh_token_expire_minutes: int = Field(
        default=60 * 24 * 7,
        alias="REFRESH_TOKEN_EXPIRE_MINUTES",
    )

    db_host: str = Field(default="db", alias="DB_HOST")
    db_port: int = Field(default=5432, alias="DB_PORT")
    db_name: str = Field(default="ems", alias="DB_NAME")
    db_user: str = Field(default="ems", alias="DB_USER")
    db_password: str = Field(default="ems", alias="DB_PASSWORD")
    database_url: str | None = Field(default=None, alias="DATABASE_URL")

    cors_origins_raw: str = Field(
        default="http://localhost:3000,http://localhost:8000",
        alias="CORS_ORIGINS",
    )
    delivery_start_required_step: Literal["PO_CREATED", "INVOICED"] = Field(
        default="PO_CREATED",
        alias="DELIVERY_START_REQUIRED_STEP",
    )

    @staticmethod
    def normalize_database_url(raw_url: str) -> str:
        normalized = raw_url.strip()
        if normalized.startswith("postgres://"):
            normalized = normalized.replace("postgres://", "postgresql://", 1)
        if normalized.startswith("postgresql://"):
            normalized = normalized.replace("postgresql://", "postgresql+psycopg://", 1)
        return normalized

    @property
    def cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins_raw.split(",") if origin.strip()]

    @property
    def sqlalchemy_database_uri(self) -> str:
        if self.database_url:
            return self.normalize_database_url(self.database_url)
        return (
            f"postgresql+psycopg://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
