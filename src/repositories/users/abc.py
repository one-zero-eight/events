__all__ = ["AbstractUserRepository"]

from abc import ABCMeta, abstractmethod

from src.app.schemas import CreateUser, ViewUser, CreateEventGroup, ViewEventGroup


class AbstractUserRepository(metaclass=ABCMeta):
    @abstractmethod
    async def create_user_if_not_exists(self, user: CreateUser) -> ViewUser:
        ...

    @abstractmethod
    async def upsert_user(self, user: CreateUser) -> ViewUser:
        ...

    @abstractmethod
    async def batch_upsert_users(self, users: list[CreateUser]) -> list[ViewUser]:
        ...

    @abstractmethod
    async def get_user_by_email(self, email: str) -> ViewUser:
        ...

    @abstractmethod
    async def batch_get_user(self, ids: list[int]) -> list[ViewUser]:
        ...

    @abstractmethod
    async def setup_groups(self, user_id: int, groups: list[int]):
        ...

    @abstractmethod
    async def batch_setup_groups(self, groups_mapping: dict[int, list[int]]):
        ...

    @abstractmethod
    async def add_favorite(
        self, email: str, favorite: CreateEventGroup
    ) -> list[ViewEventGroup]:
        ...

    @abstractmethod
    async def remove_favorite(
        self, email: str, favorite: CreateEventGroup
    ) -> list[ViewEventGroup]:
        ...

    @abstractmethod
    async def set_hidden(
        self, user_id: int, is_favorite: bool, group_id: int, hidden: bool = True
    ):
        ...

    @abstractmethod
    async def upsert_group(self, group: CreateEventGroup) -> ViewEventGroup:
        ...

    @abstractmethod
    async def batch_upsert_groups(
        self, groups: list[CreateEventGroup]
    ) -> list[ViewEventGroup]:
        ...
