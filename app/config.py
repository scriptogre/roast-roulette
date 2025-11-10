from pydantic import computed_field, PostgresDsn, model_validator
from typing import Literal, Self

import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
import sentry_sdk


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", extra="ignore", env_ignore_empty=True
    )
    """Load .env file if it exists. Ignore fields not defined in this model."""

    ENVIRONMENT: Literal["local", "production"]

    # General
    # --------------------
    PROJECT_NAME: str = "Roast Roulette"
    SECRET_KEY: str
    DEBUG: bool
    ALLOWED_HOSTS: str = "*"

    # Directories
    # --------------------
    BASE_DIR: Path = Path(__file__).resolve().parent.parent
    MEDIA_DIR: Path = BASE_DIR / "media"
    STATIC_DIR: Path = BASE_DIR / "app" / "static"
    TEMPLATES_DIR: Path = BASE_DIR / "app" / "templates"

    # Database
    # --------------------
    POSTGRES_HOST: str = "postgres"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str  # Required - must be set in .env
    POSTGRES_DB: str = "roast_roulette"

    @computed_field
    @property
    def DATABASE_URL(self) -> str:
        return str(
            PostgresDsn.build(
                scheme="postgres",
                username=self.POSTGRES_USER,
                password=self.POSTGRES_PASSWORD,
                host=self.POSTGRES_HOST,
                port=self.POSTGRES_PORT,
                path=self.POSTGRES_DB,
            )
        )

    @computed_field
    @property
    def TORTOISE_ORM(self) -> dict:
        return {
            "connections": {
                "default": str(self.DATABASE_URL),
            },
            "apps": {
                "models": {
                    "models": [
                        "aerich.models",
                        "app.models",
                    ],
                    "default_connection": "default",
                },
            },
        }

    # NATS
    # --------------------
    NATS_URL: str = "nats://nats:4222"

    # Monitoring
    # --------------------
    SENTRY_DSN: str | None = None  # Optional - set in .env for error monitoring

    # External APIs
    # --------------------
    OPENAI_API_KEY: str
    OPENAI_BASE_URL: str
    OPENAI_VISION_MODEL: str

    # Validation & Warnings
    # --------------------
    @model_validator(mode="after")
    def _ensure_directories_exist(self) -> Self:
        os.makedirs(self.BASE_DIR / "data", exist_ok=True)
        os.makedirs(self.MEDIA_DIR, exist_ok=True)
        os.makedirs(self.MEDIA_DIR / "photos", exist_ok=True)
        return self


settings = Settings()  # type: ignore

sentry_sdk.init(dsn=settings.SENTRY_DSN) if settings.SENTRY_DSN else None

TORTOISE_ORM = settings.TORTOISE_ORM  # Required for Aerich migrations
