"""
Application Configuration

Loads settings from environment variables using Pydantic Settings.
All configuration values are validated at startup.

Environment variables loaded from .env file in development.
"""

from functools import lru_cache

from pydantic import Field, PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings

    Loads from environment variables with validation.
    See .env.example for required variables.
    """

    # Database Configuration (REQUIRED)
    database_url: PostgresDsn = Field(
        ...,
        description="PostgreSQL connection string",
        examples=["postgresql://postgres:password@localhost:5432/mypersonalexaminer_dev"],
    )

    # Security Configuration (REQUIRED)
    secret_key: str = Field(
        ...,
        min_length=32,
        description="Secret key for JWT token signing (min 32 chars)",
    )

    algorithm: str = Field(
        default="HS256",
        description="JWT algorithm",
    )

    access_token_expire_minutes: int = Field(
        default=1440,  # 24 hours (constitutional requirement)
        description="JWT token expiration in minutes",
    )

    # Application Configuration
    environment: str = Field(
        default="development",
        description="Application environment (development|production)",
    )

    debug: bool = Field(
        default=True,
        description="Debug mode (disable in production)",
    )

    # API Configuration
    api_v1_prefix: str = Field(
        default="/api",
        description="API v1 route prefix",
    )

    project_name: str = Field(
        default="My Personal Examiner API",
        description="Project name for documentation",
    )

    version: str = Field(
        default="0.1.0",
        description="API version",
    )

    # CORS Configuration (Phase IV - Frontend)
    cors_origins: list[str] = Field(
        default=["http://localhost:3000"],
        description="Allowed CORS origins",
    )

    # AI Integration (Phase III+)
    openai_api_key: str | None = Field(
        default=None,
        description="OpenAI API key (Phase III)",
    )

    anthropic_api_key: str | None = Field(
        default=None,
        description="Anthropic API key (Phase III)",
    )

    # Logging
    log_level: str = Field(
        default="INFO",
        description="Logging level (DEBUG|INFO|WARNING|ERROR|CRITICAL)",
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @property
    def database_url_str(self) -> str:
        """
        Get database URL as string

        Needed for SQLAlchemy engine creation.
        """
        return str(self.database_url)

    @property
    def is_production(self) -> bool:
        """Check if running in production environment"""
        return self.environment.lower() == "production"

    @property
    def is_development(self) -> bool:
        """Check if running in development environment"""
        return self.environment.lower() == "development"


@lru_cache
def get_settings() -> Settings:
    """
    Get cached settings instance

    Uses lru_cache to ensure settings are loaded only once.
    Call this function to access settings throughout the application.

    Returns:
        Settings: Application settings instance

    Example:
        >>> from src.config import get_settings
        >>> settings = get_settings()
        >>> print(settings.database_url)
    """
    return Settings()


# Global settings instance for convenience
settings = get_settings()
