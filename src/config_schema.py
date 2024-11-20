from enum import StrEnum
from pathlib import Path

import yaml
from pydantic import BaseModel, ConfigDict, Field, SecretStr


class Environment(StrEnum):
    DEVELOPMENT = "development"
    PRODUCTION = "production"
    TESTING = "testing"


class SettingsEntityModel(BaseModel):
    model_config = ConfigDict(use_attribute_docstrings=True, extra="forbid")


class MusicRoom(SettingsEntityModel):
    """InNoHassle-MusicRoom integration settings"""

    api_url: str
    "URL of the Music Room API"
    api_key: SecretStr
    "API key for the Music Room API"


class Sport(SettingsEntityModel):
    """Innopolis Sport integration settings"""

    api_url: str = "https://sport.innopolis.university/api"
    "URL of the Sport API"


class Accounts(SettingsEntityModel):
    """InNoHassle Accounts integration settings"""

    api_url: str = "https://api.innohassle.ru/accounts/v0"
    "URL of the Accounts API"
    api_jwt_token: SecretStr
    "JWT token for accessing the Accounts API as a service"


class Settings(SettingsEntityModel):
    """Settings for the application. Get settings from `settings.yaml` file."""

    app_root_path: str = ""
    "Prefix for the API path (e.g. '/api/v0')"
    environment: Environment = Environment.DEVELOPMENT
    "App environment"
    db_url: SecretStr = Field(
        examples=[
            "postgresql+asyncpg://postgres:postgres@localhost:5432/postgres",
            "postgresql+asyncpg://postgres:postgres@db:5432/postgres",
        ]
    )
    "PostgreSQL database connection URL"
    cors_allow_origin_regex: str = ".*"
    "Allowed origins for CORS: from which domains requests to the API are allowed. Specify as a regex: `https://.*.innohassle.ru`"
    predefined_dir: Path = Path("./predefined")
    "Path to the directory with predefined data"
    accounts: Accounts
    "InNoHassle Accounts integration settings"
    music_room: MusicRoom | None = None
    "InNoHassle MusicRoom integration settings"
    sport: Sport = Sport()
    "Innopolis Sport integration settings"

    @classmethod
    def from_yaml(cls, path: Path) -> "Settings":
        with open(path, encoding="utf-8") as f:
            yaml_config: dict = yaml.safe_load(f)
            yaml_config.pop("$schema", None)

        return cls.parse_obj(yaml_config)

    @classmethod
    def save_schema(cls, path: Path) -> None:
        with open(path, "w", encoding="utf-8") as f:
            schema = {"$schema": "https://json-schema.org/draft-07/schema", **cls.model_json_schema()}
            schema["properties"]["$schema"] = {
                "description": "Path to the schema file",
                "title": "Schema",
                "type": "string",
            }
            yaml.dump(schema, f, sort_keys=False)
