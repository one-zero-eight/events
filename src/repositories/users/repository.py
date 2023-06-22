import json
from pathlib import Path

from pydantic import BaseModel, Field
from pydantic.tools import parse_obj_as

from src.app.users.schemas import CreateUser, CreateFavorite
from src.repositories.users.models import InJsonUser, InJsonFavorite


class UserStorage(BaseModel):
    users: list[InJsonUser] = Field(default_factory=list)

    def append(self, user: InJsonUser):
        self.users.append(user)

    def save_json(self, file_path: Path):
        with open(file_path, "w", encoding="utf-8") as f:
            js = self.json(indent=4, ensure_ascii=False)
            f.write(js)

    def update_from_file(self, file_path: Path):
        with open(file_path, "r", encoding="utf-8") as f:
            users_dict = json.load(f)
        users = users_dict["users"]
        # update fields
        for user in users:
            email = user["email"]
            for existing_user in self.users:
                if existing_user.email == email:
                    existing_user.favorites = user["favorites"]
                    break


class UserRepository:
    file_path: Path
    user_storage: UserStorage

    def __init__(self, file_path: Path, base_file_path: Path = None):
        self.file_path = file_path
        if base_file_path is not None:
            self.user_storage = self._load_users(base_file_path)
            self.user_storage.update_from_file(file_path)
        else:
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

    def _create_user(self, user: InJsonUser) -> InJsonUser:
        self.user_storage.append(user)
        self._save_users()
        return user

    def create_user(self, user: CreateUser) -> InJsonUser:
        # ensure that user with such email does not exist
        in_json_user = InJsonUser(**user.dict())
        return self._create_user(in_json_user)

    def update_user(self, email: str, **kwargs) -> InJsonUser:
        user = self._get_user_by_email(email)
        for key, value in kwargs.items():
            setattr(user, key, value)
        self._save_users()
        return user

    def update_or_create_user(self, email: str, **kwargs) -> InJsonUser:
        try:
            return self.update_user(email, **kwargs)
        except ValueError:
            return self._create_user(InJsonUser(email=email, **kwargs))

    def _save_users(self):
        self.user_storage.save_json(self.file_path)

    def extend_favorites(
        self, email: str, *favorites: CreateFavorite
    ) -> list[InJsonFavorite]:
        user = self._get_user_by_email(email)
        favorites = list(map(lambda f: InJsonFavorite(**f.dict()), favorites))
        user.favorites.extend(favorites)
        self._save_users()
        return user.favorites

    def delete_favorites(
        self, email: str, *favorite_names: str
    ) -> list[InJsonFavorite]:
        user = self._get_user_by_email(email)
        user.favorites = list(
            filter(lambda f: f.name not in favorite_names, user.favorites)
        )
        self._save_users()
        return user.favorites
