from src.config import settings
from src.repositories.users.repository import UserRepository

user_repository = UserRepository(settings.USERS_JSON_PATH)


def get_user_repository() -> UserRepository:
    return user_repository
