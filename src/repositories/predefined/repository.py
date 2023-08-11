__all__ = ["PredefinedRepository", "JsonUserStorage", "JsonGroupStorage", "JsonTagStorage"]

from pathlib import Path
from typing import Optional

from pydantic import BaseModel, Field, parse_obj_as
from pydantic import validator
from src.config import settings


class JsonUserStorage(BaseModel):
    class InJsonUser(BaseModel):
        email: str
        groups: list[str] = Field(default_factory=list)

    users: list[InJsonUser] = Field(default_factory=list)

    @validator("users", pre=True, each_item=True, always=True)
    def _validate_user(cls, v):
        if isinstance(v, dict):
            return JsonUserStorage.InJsonUser(**v)
        return v


class JsonGroupStorage(BaseModel):
    class PredefinedGroup(BaseModel):
        class TagReference(BaseModel):
            alias: str
            type: str

        alias: str
        name: Optional[str]
        path: Optional[str]
        description: Optional[str]
        tags: list[TagReference] = Field(default_factory=list)

    event_groups: list[PredefinedGroup] = Field(default_factory=list)

    @validator("event_groups", pre=True, each_item=True, always=True)
    def _validate_group(cls, v):
        if isinstance(v, dict):
            return JsonGroupStorage.PredefinedGroup(**v)
        return v


class JsonTagStorage(BaseModel):
    class Tag(BaseModel):
        alias: str
        name: str
        type: str

    tags: list[Tag] = Field(default_factory=list)

    @validator("tags", pre=True, each_item=True, always=True)
    def _validate_tag(cls, v):
        if isinstance(v, dict):
            return JsonTagStorage.Tag(**v)
        return v


class PredefinedRepository:
    user_storage: JsonUserStorage
    event_group_storage: JsonGroupStorage
    tag_storage: JsonTagStorage

    def __init__(
        self, user_storage: JsonUserStorage, event_group_storage: JsonGroupStorage, tag_storage: JsonTagStorage
    ):
        self.user_storage = user_storage
        self.event_group_storage = event_group_storage
        self.tag_storage = tag_storage

    @classmethod
    def from_jsons(cls, user_json: dict, event_group_json: dict, tag_json: dict):
        user_storage = parse_obj_as(JsonUserStorage, user_json)
        event_group_storage = parse_obj_as(JsonGroupStorage, event_group_json)
        tag_storage = parse_obj_as(JsonTagStorage, tag_json)
        return cls(user_storage, event_group_storage, tag_storage)

    def get_users(self) -> list[JsonUserStorage.InJsonUser]:
        return self.user_storage.users.copy()

    def get_event_groups(self) -> list[JsonGroupStorage.PredefinedGroup]:
        return self.event_group_storage.event_groups.copy()

    def get_tags(self) -> list[JsonTagStorage.Tag]:
        return self.tag_storage.tags.copy()

    @staticmethod
    def locate_ics_by_path(path: str) -> Path:
        return settings.PREDEFINED_ICS_DIR / path
