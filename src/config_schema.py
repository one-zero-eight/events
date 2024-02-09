from enum import StrEnum
from pathlib import Path

import yaml
from pydantic import BaseModel, SecretStr, Field


class Environment(StrEnum):
    DEVELOPMENT = "development"
    PRODUCTION = "production"
    TESTING = "testing"


class Settings(BaseModel):
    """
    Settings for the application. Get settings from .env file.
    """

    # Prefix for the API path (e.g. "/api/v0")
    app_root_path: str = ""

    # App environment
    environment: Environment = Environment.DEVELOPMENT

    # You can run 'openssl rand -hex 32' to generate keys
    session_secret_key: SecretStr
    jwt_private_key: SecretStr = Field(
        ...,
        description="Private key for JWT. Use 'openssl genrsa -out private.pem 2048' to generate keys",
    )
    jwt_public_key: str = Field(
        ...,
        description="Public key for JWT. Use 'openssl rsa -in private.pem -pubout -out public.pem' to generate keys",
    )

    # PostgreSQL database connection URL
    db_url: SecretStr

    # Security
    cors_allow_origins: list[str] = [
        "https://innohassle.ru",
        "https://dev.innohassle.ru",
        "https://pre.innohassle.ru",
        "http://localhost:3000",
    ]

    # Authentication
    auth_cookie_name: str = "token"
    auth_cookie_domain: str = "innohassle.ru" if environment == Environment.PRODUCTION else "localhost"
    auth_allowed_domains: list[str] = [
        "innohassle.ru",
        "api.innohassle.ru",
        "pre.innohassle.ru",
        "dev.innohassle.ru",
        "localhost",
    ]

    # Use these only in production
    innopolis_sso_client_id: SecretStr = ""
    innopolis_sso_client_secret: SecretStr = ""
    innopolis_sso_redirect_uri: str = "https://innohassle.campus.innopolis.university/oauth2/callback"

    # Use dev auth while development
    dev_auth_email: str = ""

    predefined_dir: Path = Path("./predefined")

    @classmethod
    def from_yaml(cls, path: Path) -> "Settings":
        with open(path, "r", encoding="utf-8") as f:
            yaml_config = yaml.safe_load(f)

        return cls.from_orm(yaml_config)

    @classmethod
    def save_schema(cls, path: Path) -> None:
        with open(path, "w", encoding="utf-8") as f:
            schema = {"$schema": "http://json-schema.org/draft-07/schema#", **cls.schema()}
            yaml.dump(schema, f, sort_keys=False)
