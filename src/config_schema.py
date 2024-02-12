from enum import StrEnum
from pathlib import Path
from typing import Optional

import yaml
from pydantic import BaseModel, SecretStr, root_validator, EmailStr


class Environment(StrEnum):
    DEVELOPMENT = "development"
    PRODUCTION = "production"
    TESTING = "testing"


class MusicRoom(BaseModel):
    """InNoHassle-MusicRoom integration settings"""

    api_url: str
    "URL of the Music Room API"
    token: SecretStr
    "Token for the Music Room API"


class InnopolisSSO(BaseModel):
    """Innopolis SSO settings (only for production)"""

    client_id: str
    "Client ID for Innopolis SSO"
    client_secret: SecretStr
    "Client secret for Innopolis SSO"
    redirect_uri: str = "https://innohassle.campus.innopolis.university/oauth2/callback"
    "Redirect URI for Innopolis SSO"
    resource_id: Optional[str] = None
    "Resource ID for Innopolis SSO (optional); Used for Sports API access"


class Authentication(BaseModel):
    cookie_name: str = "token"
    "Name of the cookie for authentication JWT token"
    cookie_domain: str = "localhost"
    "Domain of the cookie for authentication JWT token"
    allowed_domains: list[str] = ["localhost"]
    "Allowed domains for redirecting after authentication"
    jwt_private_key: SecretStr
    "Private key for JWT. Use 'openssl genrsa -out private.pem 2048' to generate keys"
    jwt_public_key: str
    "Public key for JWT. Use 'openssl rsa -in private.pem -pubout -out public.pem' to generate keys"
    session_secret_key: SecretStr
    "Secret key for sessions. Use 'openssl rand -hex 32' to generate keys"


class Settings(BaseModel):
    """
    Settings for the application. Get settings from `settings.yaml` file.
    """

    app_root_path: str = ""
    "Prefix for the API path (e.g. '/api/v0')"
    environment: Environment = Environment.DEVELOPMENT
    "App environment"
    db_url: SecretStr = "postgresql://postgres:postgres@localhost:5432/postgres"
    "PostgreSQL database connection URL"
    cors_allow_origins: list[str] = ["https://innohassle.ru", "https://pre.innohassle.ru", "http://localhost:3000"]
    "Allowed origins for CORS: from which domains requests to the API are allowed"
    auth: Authentication
    "Authentication settings"
    innopolis_sso: Optional[InnopolisSSO] = None
    "Innopolis SSO settings (only for production)"
    test_user_email: Optional[EmailStr] = None
    "Email for dev auth"
    predefined_dir: Path = Path("./predefined")
    "Path to the directory with predefined data"

    @classmethod
    def from_yaml(cls, path: Path) -> "Settings":
        with open(path, "r", encoding="utf-8") as f:
            yaml_config = yaml.safe_load(f)

        return cls.parse_obj(yaml_config)

    @classmethod
    def save_schema(cls, path: Path) -> None:
        with open(path, "w", encoding="utf-8") as f:
            schema = {"$schema": "http://json-schema.org/draft-07/schema#", **cls.schema()}
            yaml.dump(schema, f, sort_keys=False)

    @root_validator()
    def validate_test_user_email(cls, values):
        test_user_email = values.get("test_user_email")
        if test_user_email is None and values["environment"] == Environment.DEVELOPMENT:
            raise ValueError("test_user_email must be set in development environment")
        return values
