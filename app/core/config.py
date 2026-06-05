from functools import lru_cache
from typing import Annotated

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "FYFIT Backend"
    app_env: str = "local"
    api_v1_prefix: str = "/api/v1"
    database_url: str = "postgresql+asyncpg://fyfit:fyfit@localhost:5432/fyfit"
    sync_database_url: str = "postgresql+psycopg://fyfit:fyfit@localhost:5432/fyfit"
    redis_url: str = "redis://localhost:6379/0"
    firebase_project_id: str | None = None
    firebase_credentials_json: str | None = None
    openai_api_key: str | None = None
    anthropic_api_key: str | None = None
    cors_origins: Annotated[list[str], NoDecode] = Field(
        default_factory=lambda: ["http://localhost:3000"]
    )
    rate_limit_per_minute: int = 120

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, value: str | list[str]) -> list[str]:
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
