__all__ = ["SqlEventGroupRepository"]

from typing import Optional

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as postgres_insert
from sqlalchemy.ext.asyncio import AsyncSession

from src.repositories.crud import CRUDFactory, AbstractCRUDRepository
from src.repositories.ownership import setup_ownership_method
from src.schemas import ViewEventGroup, CreateEventGroup, UpdateEventGroup, OwnershipEnum
from src.storages.sql import SQLAlchemyStorage
from src.storages.sql.models import UserXFavoriteEventGroup, EventGroup

CRUD: AbstractCRUDRepository[
    CreateEventGroup,
    ViewEventGroup,
    UpdateEventGroup,
] = CRUDFactory(
    EventGroup,
    CreateEventGroup,
    ViewEventGroup,
    UpdateEventGroup,
)


class SqlEventGroupRepository:
    storage: SQLAlchemyStorage

    def __init__(self, storage: SQLAlchemyStorage):
        self.storage = storage

    def _create_session(self) -> AsyncSession:
        return self.storage.create_session()

    # ----------------- CRUD ----------------- #

    async def create(self, group: CreateEventGroup) -> ViewEventGroup:
        async with self._create_session() as session:
            return await CRUD.create(session, group)

    async def batch_create(self, groups: list[CreateEventGroup]) -> list[ViewEventGroup]:
        async with self._create_session() as session:
            return await CRUD.batch_create(session, groups)

    async def read(self, group_id: int) -> ViewEventGroup:
        async with self._create_session() as session:
            return await CRUD.read(session, id=group_id)

    async def get_only_path(self, group_id: int) -> Optional[str]:
        async with self._create_session() as session:
            q = select(EventGroup.path).where(EventGroup.id == group_id).where(EventGroup.path.isnot(None))
            path: Optional[str] = await session.scalar(q)
            return path

    async def read_all(self) -> list[ViewEventGroup]:
        async with self._create_session() as session:
            return await CRUD.read_all(session)

    async def batch_read(self, group_ids: list[int]) -> list[ViewEventGroup]:
        async with self._create_session() as session:
            return await CRUD.batch_read(session, pkeys=[{"id": group_id} for group_id in group_ids])

    async def read_by_path(self, path: str) -> ViewEventGroup:
        async with self._create_session() as session:
            return await CRUD.read_by(session, only_first=True, path=path)

    async def read_by_alias(self, alias: str) -> ViewEventGroup:
        async with self._create_session() as session:
            return await CRUD.read_by(session, only_first=True, alias=alias)

    async def update(self, event_group_id: int, event_group: UpdateEventGroup) -> ViewEventGroup:
        async with self._create_session() as session:
            return await CRUD.update(session, data=event_group, id=event_group_id)

    async def batch_update(self, event_groups: dict[int, "UpdateEventGroup"]) -> list["ViewEventGroup"]:
        async with self._create_session() as session:
            data = list(event_groups.values())

            return await CRUD.batch_update(
                session, data=data, pkeys=[{"id": event_group_id} for event_group_id in event_groups.keys()]
            )

    # ^^^^^^^^^^^^^^^^^ CRUD ^^^^^^^^^^^^^^^^^ #

    async def setup_ownership(self, group_id: int, user_id: int, role_alias: "OwnershipEnum") -> None:
        async with self._create_session() as session:
            OwnershipClass = EventGroup.Ownership
            return await setup_ownership_method(OwnershipClass, session, group_id, user_id, role_alias)

    async def setup_groups(self, user_id: int, groups: list[int]):
        async with self._create_session() as session:
            q = (
                postgres_insert(UserXFavoriteEventGroup)
                .values([{"user_id": user_id, "group_id": group_id, "predefined": True} for group_id in groups])
                .on_conflict_do_update(
                    index_elements=[UserXFavoriteEventGroup.user_id, UserXFavoriteEventGroup.group_id],
                    set_={"predefined": True},
                )
            )
            await session.execute(q)
            await session.commit()

    async def batch_setup_groups(self, groups_mapping: dict[int, list[int]]):
        async with self._create_session() as session:
            # in one query
            q = (
                postgres_insert(UserXFavoriteEventGroup)
                .values(
                    [
                        {"user_id": user_id, "group_id": group_id, "predefined": True}
                        for user_id, group_ids in groups_mapping.items()
                        for group_id in group_ids
                    ]
                )
                .on_conflict_do_update(
                    index_elements=[UserXFavoriteEventGroup.user_id, UserXFavoriteEventGroup.group_id],
                    set_={"predefined": True},
                )
            )
            await session.execute(q)
            await session.commit()
