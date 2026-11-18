import warnings
from pydantic_settings import BaseSettings, SettingsConfigDict


_DEFAULT_SECRET = "your_secret_key_here"


class Settings(BaseSettings):
    PROJECT_NAME: str = "OTT Content Aggregator API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"

    # PostgreSQL Database URL loaded from environment variable (.env)
    # Generic placeholder used as default; no real credentials are hardcoded
    DATABASE_URL: str = (
        "postgresql://username:password@localhost:5432/ott_aggregator"
    )

    # JWT Authentication settings (for M2)
    SECRET_KEY: str = _DEFAULT_SECRET
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Redis Cache settings (for Week 3)
    REDIS_URL: str = "redis://localhost:6379/0"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()

# Emit a loud warning when running with the insecure default secret
if settings.SECRET_KEY == _DEFAULT_SECRET:
    warnings.warn(
        "⚠  SECRET_KEY is set to the public default value. "
        "Set a strong, unique SECRET_KEY in your .env file or environment variables "
        "before deploying to production.",
        stacklevel=1,
    )
