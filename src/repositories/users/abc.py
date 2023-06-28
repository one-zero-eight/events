__all__ = ["AbstractUserRepository", "USER_ID"]

from abc import ABCMeta, abstractmethod
from typing import Annotated

from src.app.schemas import CreateUser, ViewUser, CreateEventGroup, ViewEventGroup
from src.storages.sql.models import UserXGroup

USER_ID = Annotated[int, "User ID"]


class AbstractUserRepository(metaclass=ABCMeta):
    @abstractmethod
    async def create_user_if_not_exists(self, user: CreateUser) -> ViewUser:
        ...

    @abstractmethod
    async def batch_create_user_if_not_exists(
        self, users: list[CreateUser]
    ) -> list[ViewUser]:
        ...

    @abstractmethod
    async def get_user_id_by_email(self, email: str) -> USER_ID:
        ...

    @abstractmethod
    async def get_user(self, user_id: USER_ID) -> ViewUser:
        ...

    @abstractmethod
    async def batch_get_user(self, ids: list[USER_ID]) -> list[ViewUser]:
        ...

    @abstractmethod
    async def setup_groups(self, user_id: USER_ID, groups: list[int]):
        ...

    @abstractmethod
    async def batch_setup_groups(self, groups_mapping: dict[USER_ID, list[int]]):
        ...

    @abstractmethod
    async def add_favorite(
        self, user_id: USER_ID, favorite_id: int
    ) -> list[UserXGroup]:
        ...

    @abstractmethod
    async def remove_favorite(
        self, user_id: USER_ID, favorite_id: int
    ) -> list[UserXGroup]:
        ...

    @abstractmethod
    async def set_hidden(
        self, user_id: USER_ID, is_favorite: bool, group_id: int, hide: bool = True
    ) -> list[UserXGroup]:
        ...

    @abstractmethod
    async def get_group(self, group_id: int) -> ViewEventGroup:
        ...

    @abstractmethod
    async def create_group_if_not_exists(
        self, group: CreateEventGroup
    ) -> ViewEventGroup:
        ...

    @abstractmethod
    async def batch_create_group_if_not_exists(
        self, groups: list[CreateEventGroup]
    ) -> list[ViewEventGroup]:
        ...
