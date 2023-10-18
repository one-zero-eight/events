__all__ = ["AbstractUserRepository"]

from abc import ABCMeta, abstractmethod
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from src.schemas import CreateUser, ViewUser, LinkedCalendarCreate, LinkedCalendarView


class AbstractUserRepository(metaclass=ABCMeta):
    # ----------------- CRUD ----------------- #
    @abstractmethod
    async def create_or_read(self, user: "CreateUser") -> "ViewUser":
        ...

    @abstractmethod
    async def batch_create_or_read(self, users: list["CreateUser"]) -> list["ViewUser"]:
        ...

    @abstractmethod
    async def create_or_update(self, user: "CreateUser") -> "ViewUser":
        ...

    @abstractmethod
    async def read(self, user_id: int) -> "ViewUser":
        ...

    @abstractmethod
    async def read_id_by_email(self, email: str) -> int:
        ...

    @abstractmethod
    async def batch_read(self, ids: list[int]) -> list["ViewUser"]:
        ...

    # ^^^^^^^^^^^^^^^^^ CRUD ^^^^^^^^^^^^^^^^^^^^^^^^ #

    @abstractmethod
    async def add_favorite(self, user_id: int, favorite_id: int) -> "ViewUser":
        ...

    @abstractmethod
    async def remove_favorite(self, user_id: int, favorite_id: int) -> "ViewUser":
        ...

    @abstractmethod
    async def set_hidden(self, user_id: int, group_id: int, hide: bool = True) -> "ViewUser":
        ...

    @abstractmethod
    async def link_calendar(self, user_id: int, calendar: "LinkedCalendarCreate") -> "LinkedCalendarView":
        ...
