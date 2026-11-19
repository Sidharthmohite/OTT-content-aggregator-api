import warnings
from pydantic_settings import BaseSettings, SettingsConfigDict


_DEFAULT_SECRET = "your_secret_key_here"
_INSECURE_SECRETS = {
    _DEFAULT_SECRET,
    "secret",
    "secret_key",
    "changeme",
    "password",
    "admin",
    "",
}


def check_secret_key_security(secret_key: str) -> bool:
    """Check if the SECRET_KEY is default, insecure, or too weak.

    Emits a UserWarning if the key is insecure.
    Returns True if a warning was emitted, False if secure.
    """
    if not secret_key or secret_key in _INSECURE_SECRETS or len(secret_key) < 32:
        warnings.warn(
            "⚠  SECRET_KEY is set to a default or weak value. "
            "Set a strong, random SECRET_KEY of at least 32 characters in your .env file "
            "or environment variables before deploying to production.",
            category=UserWarning,
            stacklevel=2,
        )
        return True
    return False


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

# Check and warn if using default/weak secret
check_secret_key_security(settings.SECRET_KEY)
