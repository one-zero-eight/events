__all__ = ["AbstractEventGroupRepository"]

from abc import ABCMeta, abstractmethod
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from src.schemas import CreateEventGroup, ViewEventGroup, OwnershipEnum, UpdateEventGroup


class AbstractEventGroupRepository(metaclass=ABCMeta):
    # ----------------- CRUD ----------------- #
    @abstractmethod
    async def create(self, group: "CreateEventGroup") -> "ViewEventGroup":
        ...

    @abstractmethod
    async def batch_create(self, groups: list["CreateEventGroup"]) -> list["ViewEventGroup"]:
        ...

    @abstractmethod
    async def read(self, group_id: int) -> "ViewEventGroup":
        ...

    @abstractmethod
    async def read_all(self) -> list["ViewEventGroup"]:
        ...

    @abstractmethod
    async def batch_read(self, group_ids: list[int]) -> list["ViewEventGroup"]:
        ...

    @abstractmethod
    async def read_by_path(self, path: str) -> "ViewEventGroup":
        ...

    @abstractmethod
    async def read_by_alias(self, alias: str) -> "ViewEventGroup":
        ...

    @abstractmethod
    async def update(self, event_group_id: int, event_group: "UpdateEventGroup") -> "ViewEventGroup":
        ...

    @abstractmethod
    async def batch_update(self, event_groups: dict[int, "UpdateEventGroup"]) -> list["ViewEventGroup"]:
        ...

    # ^^^^^^^^^^^^^^^^^ CRUD ^^^^^^^^^^^^^^^^^^^^^^^^ #

    @abstractmethod
    async def get_only_path(self, group_id: int) -> Optional[str]:
        ...

    @abstractmethod
    async def setup_ownership(self, group_id: int, user_id: int, role_alias: "OwnershipEnum") -> None:
        ...

    @abstractmethod
    async def setup_groups(self, user_id: int, groups: list[int]):
        ...

    @abstractmethod
    async def batch_setup_groups(self, groups_mapping: dict[int, list[int]]):
        ...
