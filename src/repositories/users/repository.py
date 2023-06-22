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
                return user.copy()
        raise ValueError(f"User with email {email} not found")

    def create_user(self, user: InJsonUser):
        # ensure that user with such email does not exist
        self.users.append(user)
        self._save_users()

    def update_user(self, email: str, **kwargs):
        user = self.get_user_by_email(email)
        for key, value in kwargs.items():
            setattr(user, key, value)
        self._save_users()

    def update_or_create_user(self, email: str, **kwargs):
        try:
            self.update_user(email, **kwargs)
        except ValueError:
            self.create_user(InJsonUser(email=email, **kwargs))

    def _save_users(self):
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(self.users, f, indent=4)
