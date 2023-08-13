__all__ = ["AbstractWorkshopRepository"]

from abc import ABCMeta, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.schemas import CreateWorkshop, ViewWorkshop, UpdateTag, CheckIn  # noqa: F401


class AbstractWorkshopRepository(
    metaclass=ABCMeta,
):
    # ----------------- CRUD ----------------- #
    @abstractmethod
    async def create_or_update(self, workshop: "CreateWorkshop") -> "ViewWorkshop":
        ...

    @abstractmethod
    async def read(self, id: int) -> "ViewWorkshop":
        ...

    @abstractmethod
    async def read_all(self) -> list["ViewWorkshop"]:
        ...

    @abstractmethod
    async def read_by_alias(self, alias: str) -> "ViewWorkshop":
        ...

    # ^^^^^^^^^^^^^^^^^ CRUD ^^^^^^^^^^^^^^^^^^^^^^^^ #
