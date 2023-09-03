__all__ = ["AbstractTagRepository"]

from abc import ABCMeta, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.schemas import CreateTag, ViewTag, UpdateTag, OwnershipEnum


class AbstractTagRepository(
    metaclass=ABCMeta,
):
    # ----------------- CRUD ----------------- #
    @abstractmethod
    async def create_or_read(self, tag: "CreateTag") -> "ViewTag":
        ...

    @abstractmethod
    async def batch_create_or_read(self, tags: list["CreateTag"]) -> list["ViewTag"]:
        ...

    @abstractmethod
    async def read(self, id: int) -> "ViewTag":
        ...

    @abstractmethod
    async def read_all(self) -> list["ViewTag"]:
        ...

    @abstractmethod
    async def batch_read(self, tag_ids: list[int]) -> list["ViewTag"]:
        ...

    @abstractmethod
    async def read_by_name(self, name: str) -> "ViewTag":
        ...

    @abstractmethod
    async def update(self, id: int, tag: "UpdateTag") -> "ViewTag":
        ...

    @abstractmethod
    async def delete(self, id: int) -> None:
        ...

    # ^^^^^^^^^^^^^^^^^ CRUD ^^^^^^^^^^^^^^^^^^^^^^^^ #

    @abstractmethod
    async def setup_ownership(self, tag_id: int, user_id: int, role_alias: "OwnershipEnum") -> None:
        ...

    @abstractmethod
    async def add_tags_to_event_group(self, event_group_id: int, tag_ids: list[int]) -> None:
        ...

    @abstractmethod
    async def batch_set_tags_to_event_group(self, tags_mapping: dict[int, list[int]]) -> None:
        ...

    @abstractmethod
    async def remove_tags_from_event_group(self, event_group_id: int, tag_ids: list[int]) -> None:
        ...
