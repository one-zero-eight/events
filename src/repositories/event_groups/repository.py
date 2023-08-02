__all__ = ["SqlEventGroupRepository"]

from sqlalchemy.dialects.postgresql import insert as postgres_insert
from sqlalchemy.ext.asyncio import AsyncSession

from src.repositories.crud import CRUDFactory
from src.repositories.event_groups.abc import AbstractEventGroupRepository
from src.repositories.ownership import setup_ownership_method
from src.schemas import ViewEventGroup, CreateEventGroup, UpdateEventGroup, OwnershipEnum
from src.storages.sql import AbstractSQLAlchemyStorage
from src.storages.sql.models import UserXFavoriteEventGroup, EventGroup

CRUD = CRUDFactory(
    EventGroup,
    CreateEventGroup,
    ViewEventGroup,
    UpdateEventGroup,
)


class SqlEventGroupRepository(AbstractEventGroupRepository):
    storage: AbstractSQLAlchemyStorage

    def __init__(self, storage: AbstractSQLAlchemyStorage):
        self.storage = storage

    def _create_session(self) -> AsyncSession:
        return self.storage.create_session()

    # ----------------- CRUD ----------------- #
    async def read(self, group_id: int) -> ViewEventGroup:
        async with self._create_session() as session:
            return await CRUD.read(session, id=group_id)

    async def read_all(self) -> list[ViewEventGroup]:
        async with self._create_session() as session:
            return await CRUD.read_all(session)

    async def read_by_path(self, path: str) -> ViewEventGroup:
        async with self._create_session() as session:
            return await CRUD.read_by(session, only_first=True, path=path)

    async def create_or_read(self, group: CreateEventGroup) -> ViewEventGroup:
        async with self._create_session() as session:
            created = await CRUD.create_if_not_exists(session, group)
            if created is None:
                created = await CRUD.read_by(session, only_first=True, path=group.path)
            return created

    async def batch_create_or_read(self, groups: list[CreateEventGroup]) -> list[ViewEventGroup]:
        async with self._create_session() as session:
            q = (
                postgres_insert(EventGroup)
                .values([group.dict() for group in groups])
                .on_conflict_do_update(
                    index_elements=[EventGroup.alias],
                    set_={"id": EventGroup.id},
                )
                .returning(EventGroup)
            )
            db_groups = await session.scalars(q)
            await session.commit()
            return [ViewEventGroup.from_orm(group) for group in db_groups]

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
