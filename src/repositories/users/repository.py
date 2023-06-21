import json
from pathlib import Path

from pydantic.tools import parse_obj_as

from src.repositories.users.models import InJsonUser


class UserRepository:
    file_path: Path
    users: list[InJsonUser]

    def __init__(self, file_path: Path):
        self.file_path = file_path
        self.users = self._load_users(file_path)

    @staticmethod
    def _load_users(file_path: Path) -> list[InJsonUser]:
        with open(file_path, "r", encoding="utf-8") as f:
            users_list = json.load(f)
        return parse_obj_as(list[InJsonUser], users_list)

    def get_users(self):
        return self.users

    def get_user_by_email(self, email: str) -> InJsonUser:
        for user in self.users:
            if user.email == email:
                return user
        raise ValueError(f"User with email {email} not found")
