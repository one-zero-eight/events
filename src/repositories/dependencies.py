from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.repositories.users import AbstractUserRepository
    from src.repositories.event_groups import AbstractEventGroupRepository
    from src.storages.sql.storage import AbstractSQLAlchemyStorage


class Dependencies:
    _storage: "AbstractSQLAlchemyStorage"
    _user_repository: "AbstractUserRepository"
    _event_group_repository: "AbstractEventGroupRepository"

    @classmethod
    def get_storage(cls) -> "AbstractSQLAlchemyStorage":
        return cls._storage

    @classmethod
    def set_storage(cls, storage: "AbstractSQLAlchemyStorage"):
        cls._storage = storage

    @classmethod
    def get_user_repository(cls) -> "AbstractUserRepository":
        return cls._user_repository

    @classmethod
    def set_user_repository(cls, user_repository: "AbstractUserRepository"):
        cls._user_repository = user_repository

    @classmethod
    def get_event_group_repository(cls) -> "AbstractEventGroupRepository":
        return cls._event_group_repository

    @classmethod
    def set_event_group_repository(
        cls, event_group_repository: "AbstractEventGroupRepository"
    ):
        cls._event_group_repository = event_group_repository
