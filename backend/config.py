"""Application configuration. Credentials are read from environment variables only."""
from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    cognodb_uri: str
    cognodb_username: str
    cognodb_password: str
    cognodb_database: str = "neo4j"

    api_title: str = "CareerGraph API"
    api_version: str = "1.0.0"

    cors_origins: list[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:4173",
        "https://verdant-maamoul-f10313.netlify.app",
    ]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
