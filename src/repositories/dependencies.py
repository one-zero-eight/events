from src.repositories.users import AbstractUserRepository
from src.storages.sql.storage import AbstractSQLAlchemyStorage


class Dependencies:
    _storage: AbstractSQLAlchemyStorage
    _user_repository: AbstractUserRepository

    @classmethod
    def get_storage(cls) -> AbstractSQLAlchemyStorage:
        return cls._storage

    @classmethod
    def set_storage(cls, storage: AbstractSQLAlchemyStorage):
        cls._storage = storage

    @classmethod
    def get_user_repository(cls) -> AbstractUserRepository:
        return cls._user_repository

    @classmethod
    def set_user_repository(cls, user_repository: AbstractUserRepository):
        cls._user_repository = user_repository
