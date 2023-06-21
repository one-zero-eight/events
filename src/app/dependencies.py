__all__ = ["get_current_user_email", "get_user_repository"]

from src.config import settings
from src.repositories.users.repository import UserRepository
from src.app.auth import get_current_user_email

user_repository = UserRepository(settings.USERS_JSON_PATH)


def get_user_repository() -> UserRepository:
    return user_repository
