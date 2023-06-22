__all__ = ["get_user_repository", "get_current_user_email"]

from src.config import settings
from src.repositories import UserRepository

user_repository = UserRepository(settings.INNOPOLIS_USER_DATA_PATH, settings.USERS_JSON_PATH)


def get_user_repository() -> UserRepository:
    return user_repository


from src.app.auth.dependencies import get_current_user_email
