"""
Connectivity Backend - Configuration

Environment-based configuration using pydantic-settings.
All deployment-specific values (domains, URLs) must be provided
via environment variables or a .env file — never hardcoded here.
"""

from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application
    app_name: str = "Connectivity"
    app_version: str = "1.0.0"
    debug: bool = False

    # API
    api_prefix: str = "/api/connectivity"

    # CORS — set via CORS_ORIGINS env var (comma-separated or JSON list)
    # Example: CORS_ORIGINS=["https://app.example.com","http://localhost:3000"]
    cors_origins: list[str] = [
        "http://localhost:3000",
        "http://localhost:5003",
    ]

    # Keycloak / JWT Authentication
    # Set KEYCLOAK_URL in K8s env vars or .env file — do not hardcode domain here
    keycloak_url: str = "http://keycloak:8080/auth"
    keycloak_realm: str = "nekazari"
    jwt_audience: str = "account"
    jwt_issuer: str = ""  # Auto-derived from keycloak_url + realm if empty

    # Service-to-service authentication
    module_management_key: str = ""

    # Database
    mongodb_url: str = ""

    @property
    def jwt_issuer_url(self) -> str:
        """Get the JWT issuer URL."""
        if self.jwt_issuer:
            return self.jwt_issuer
        return f"{self.keycloak_url}/realms/{self.keycloak_realm}"

    @property
    def jwks_url(self) -> str:
        """Get the JWKS URL for token verification."""
        return f"{self.jwt_issuer_url}/protocol/openid-connect/certs"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
