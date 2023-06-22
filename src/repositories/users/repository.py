import json
from pathlib import Path

from pydantic import BaseModel, Field
from pydantic.tools import parse_obj_as

from src.repositories.users.models import InJsonUser


class UserStorage(BaseModel):
    users: list[InJsonUser] = Field(default_factory=list)

    def append(self, user: InJsonUser):
        self.users.append(user)

    def save_json(self, file_path: Path):
        with open(file_path, "w", encoding="utf-8") as f:
            js = self.json(indent=4, ensure_ascii=False)
            f.write(js)


class UserRepository:
    file_path: Path
    user_storage: UserStorage

    def __init__(self, file_path: Path, out_file_path: Path):
        self.file_path = file_path
        self.out_file_path = out_file_path
        self.user_storage = self._load_users(file_path)

    @staticmethod
    def _load_users(file_path: Path) -> UserStorage:
        with open(file_path, "r", encoding="utf-8") as f:
            users_dict = json.load(f)
        return parse_obj_as(UserStorage, users_dict)

    def get_users(self) -> list[InJsonUser]:
        return self.user_storage.users.copy()

    def _get_user_by_email(self, email: str) -> InJsonUser:
        for user in self.user_storage.users:
            if user.email == email:
                return user
        raise ValueError(f"User with email {email} not found")

    def get_user_by_email(self, email: str) -> InJsonUser:
        return self._get_user_by_email(email).copy()

    def create_user(self, user: InJsonUser):
        # ensure that user with such email does not exist
        self.user_storage.append(user)
        self._save_users()

    def update_user(self, email: str, **kwargs):
        user = self._get_user_by_email(email)
        for key, value in kwargs.items():
            setattr(user, key, value)
        self._save_users()

    def update_or_create_user(self, email: str, **kwargs):
        try:
            self.update_user(email, **kwargs)
        except ValueError:
            self.create_user(InJsonUser(email=email, **kwargs))

    def _save_users(self):
        self.user_storage.save_json(self.out_file_path)

    def extend_favorites(self, email: str, *favorites: str):
        user = self.get_user_by_email(email)
        user.favorites.extend(favorites)
        self._save_users()
