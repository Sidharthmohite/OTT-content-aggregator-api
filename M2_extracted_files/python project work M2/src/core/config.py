"""Application configuration settings for the OTT Content Aggregator API.
Loads environment variables using Pydantic Settings.
"""

from typing import Optional

try:
    from pydantic_settings import BaseSettings, SettingsConfigDict
except ImportError:  # pragma: no cover
    from pydantic import BaseModel as BaseSettings
    from pydantic import ConfigDict as SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration settings."""

    # Project Information
    PROJECT_NAME: str = "OTT Content Aggregator API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"

    # PostgreSQL Database Configuration (M3)
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/ott_aggregator"

    # JWT Authentication & Security (M2)
    SECRET_KEY: str = "default_insecure_secret_key_change_me_in_production_environment"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Redis Cache Configuration (Week 3)
    REDIS_URL: str = "redis://localhost:6379/0"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


# Global singleton settings instance
settings = Settings()
