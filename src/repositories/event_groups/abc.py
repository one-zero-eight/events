__all__ = ["AbstractEventGroupRepository"]

from abc import ABCMeta, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.schemas import CreateEventGroup, ViewEventGroup, OwnershipEnum


class AbstractEventGroupRepository(metaclass=ABCMeta):
    # ----------------- CRUD ----------------- #
    @abstractmethod
    async def create_or_read(self, group: "CreateEventGroup") -> "ViewEventGroup":
        ...

    @abstractmethod
    async def batch_create_or_read(self, groups: list["CreateEventGroup"]) -> list["ViewEventGroup"]:
        ...

    @abstractmethod
    async def read(self, group_id: int) -> "ViewEventGroup":
        ...

    @abstractmethod
    async def read_all(self) -> list["ViewEventGroup"]:
        ...

    @abstractmethod
    async def read_by_path(self, path: str) -> "ViewEventGroup":
        ...

    # ^^^^^^^^^^^^^^^^^ CRUD ^^^^^^^^^^^^^^^^^^^^^^^^ #

    @abstractmethod
    async def setup_ownership(self, group_id: int, user_id: int, role_alias: "OwnershipEnum") -> None:
        ...

    @abstractmethod
    async def setup_groups(self, user_id: int, groups: list[int]):
        ...

    @abstractmethod
    async def batch_setup_groups(self, groups_mapping: dict[int, list[int]]):
        ...
