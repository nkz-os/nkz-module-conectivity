"""
Connectivity Backend - Configuration

Environment-based configuration using pydantic-settings.
The SDK (nkz-platform-sdk) handles Orion-LD URLs, auth, CORS, and logging.
"""

from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    app_name: str = "Connectivity"
    app_version: str = "1.0.0"
    debug: bool = False
    api_prefix: str = "/api/connectivity"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
