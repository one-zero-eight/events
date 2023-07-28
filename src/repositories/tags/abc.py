__all__ = ["AbstractTagRepository"]

from abc import ABCMeta, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.schemas import CreateTag, ViewTag, OwnershipEnum


class AbstractTagRepository(metaclass=ABCMeta):
    @abstractmethod
    async def get_tag(self, tag_id: int) -> "ViewTag":
        ...

    @abstractmethod
    async def get_all_tags(self) -> list["ViewTag"]:
        ...

    @abstractmethod
    async def get_tag_by_name(self, name: str) -> "ViewTag":
        ...

    @abstractmethod
    async def create_tag_if_not_exists(self, tag: "CreateTag") -> "ViewTag":
        ...

    @abstractmethod
    async def batch_create_tag_if_not_exists(self, tags: list["CreateTag"]) -> list["ViewTag"]:
        ...

    @abstractmethod
    async def get_tags_by_ids(self, tag_ids: list[int]) -> list["ViewTag"]:
        ...

    @abstractmethod
    async def setup_ownership(self, tag_id: int, user_id: int, role_alias: "OwnershipEnum") -> None:
        ...

    @abstractmethod
    async def add_tags_to_event_group(self, event_group_id: int, tag_ids: list[int]) -> None:
        ...

    @abstractmethod
    async def batch_add_tags_to_event_group(self, tags_mapping: dict[int, list[int]]) -> None:
        ...

    @abstractmethod
    async def remove_tags_from_event_group(self, event_group_id: int, tag_ids: list[int]) -> None:
        ...
