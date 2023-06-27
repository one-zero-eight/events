__all__ = ["PredefinedGroupsRepository"]

import json
from pathlib import Path
from typing import Optional

from pydantic import BaseModel, Field
from pydantic import validator, parse_obj_as


class InJsonEventGroup(BaseModel):
    """
    Represents a group instance from the predefined users json file.
    """

    name: str
    type: Optional[str]


class InJsonUser(BaseModel):
    """
    Represents a user instance from the predefined users json file.
    """

    email: str
    groups: list[InJsonEventGroup] = Field(default_factory=list)


class JsonUserStorage(BaseModel):
    users: list[InJsonUser] = Field(default_factory=list)

    def save_json(self, file_path: Path):
        with open(file_path, "w", encoding="utf-8") as f:
            js = self.json(indent=4, ensure_ascii=False)
            f.write(js)

    @validator("users", pre=True, each_item=True, always=True)
    def _validate_user(cls, v):
        if isinstance(v, dict):
            return InJsonUser(**v)
        return v


class PredefinedGroupsRepository:
    storage: JsonUserStorage

    def __init__(self, file_path: Path):
        self.file_path = file_path
        self.storage = self._load_users(file_path)

    @staticmethod
    def _load_users(file_path: Path) -> JsonUserStorage:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                users_dict = json.load(f)
        except FileNotFoundError:
            # create empty file
            with open(file_path, "w", encoding="utf-8") as f:
                f.write('{"users": []}')
            return JsonUserStorage()
        return parse_obj_as(JsonUserStorage, users_dict)

    def get_users(self) -> list[InJsonUser]:
        return self.storage.users.copy()

    def get_unique_groups(self) -> list[InJsonEventGroup]:
        groups = []
        visited = set()
        for user in self.storage.users:
            for group in user.groups:
                if group.name not in visited:
                    visited.add(group.name)
                    groups.append(group)

        return groups
