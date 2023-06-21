from pydantic import BaseSettings


class Settings(BaseSettings):
    """
    Settings for the application. Get settings from .env file.
    """

    APP_VERSION = "0.1.0"
    APP_DESCRIPTION = "InNoHassle-Events API"

    # You can run 'openssl rand -hex 32' to generate keys
    SESSION_SECRET_KEY: str
    JWT_SECRET_KEY: str

    INNOPOLIS_SSO_CLIENT_ID: str
    INNOPOLIS_SSO_CLIENT_SECRET: str

    class Config:
        env_file = ".env.local"
        env_file_encoding = "utf-8"


settings = Settings()
