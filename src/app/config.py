from pydantic import BaseSettings


class Settings(BaseSettings):
    """
    Settings for the application. Get settings from .env file.
    """

    SITE_DOMAIN: str = "api.innohassle.ru"

    APP_VERSION: str
    APP_DESCRIPTION: str = "InNoHassle-Events API"

    class Config:
        env_file = ".env.local"
        env_file_encoding = "utf-8"


settings = Settings()
