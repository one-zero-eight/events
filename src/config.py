from enum import StrEnum
from pathlib import Path

from pydantic import BaseSettings, SecretStr


class Environment(StrEnum):
    DEVELOPMENT = "development"
    PRODUCTION = "production"
    TESTING = "testing"


class Settings(BaseSettings):
    """
    Settings for the application. Get settings from .env file.
    """

    # Prefix for the API path (e.g. "/api/v0")
    APP_ROOT_PATH: str = ""

    # App environment
    ENVIRONMENT: Environment = Environment.DEVELOPMENT

    # You can run 'openssl rand -hex 32' to generate keys
    SESSION_SECRET_KEY: SecretStr
    JWT_SECRET_KEY: SecretStr

    # PostgreSQL database connection URL
    DB_URL: SecretStr

    # Security
    CORS_ALLOW_ORIGINS: list[str] = [
        "https://innohassle.ru",
        "https://dev.innohassle.ru",
        "http://localhost:3000",
    ]

    # Authentication
    AUTH_COOKIE_NAME: str = "token"
    AUTH_COOKIE_DOMAIN: str = "innohassle.ru" if ENVIRONMENT == Environment.PRODUCTION else "localhost"
    AUTH_ALLOWED_DOMAINS: list[str] = ["innohassle.ru", "api.innohassle.ru", "localhost"]

    # Use these only in production
    INNOPOLIS_SSO_CLIENT_ID: SecretStr = ""
    INNOPOLIS_SSO_CLIENT_SECRET: SecretStr = ""
    INNOPOLIS_SSO_REDIRECT_URI: str = "https://innohassle.campus.innopolis.university/oauth2/callback"

    # Use dev auth while development
    DEV_AUTH_EMAIL: str = ""

    PREDEFINED_DIR: Path = Path("./predefined")

    class Config:
        env_file = ".env.local"
        env_file_encoding = "utf-8"


settings = Settings()
