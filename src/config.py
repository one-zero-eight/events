from enum import StrEnum
from pathlib import Path

from pydantic import BaseSettings, validator, SecretStr


class Environment(StrEnum):
    DEVELOPMENT = "development"
    PRODUCTION = "production"


class Settings(BaseSettings):
    """
    Settings for the application. Get settings from .env file.
    """

    APP_TITLE = "InNoHassle Events API"
    APP_DESCRIPTION = "API of Events project in InNoHassle Ecosystem."
    APP_VERSION = "0.1.0"

    ENVIRONMENT: Environment = Environment.DEVELOPMENT

    # You can run 'openssl rand -hex 32' to generate keys
    SESSION_SECRET_KEY: SecretStr
    JWT_SECRET_KEY: SecretStr

    AUTH_REDIRECT_URI_PREFIX: str = (
        "https://innohassle.campus.innopolis.university/oauth2/callback"
    )

    # Use these only in production
    INNOPOLIS_SSO_CLIENT_ID: SecretStr = ""
    INNOPOLIS_SSO_CLIENT_SECRET: SecretStr = ""

    # Use dev auth while development
    DEV_AUTH_EMAIL: str = ""

    USERS_JSON_PATH: Path = Path("src/repositories/users/users.json")
    INNOPOLIS_USER_DATA_PATH: Path = Path(
        "src/repositories/users/innopolis_user_data.json"
    )

    @validator("USERS_JSON_PATH", pre=True, always=True)
    def set_relative_path(cls, v):
        v = Path(v)
        if not v.is_absolute():
            v = Path(__file__).parent.parent / v
        return v

    class Config:
        env_file = ".env.local"
        env_file_encoding = "utf-8"


settings = Settings()
