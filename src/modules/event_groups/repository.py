__all__ = ["SqlEventGroupRepository", "event_group_repository"]

from typing import Iterable, Optional, cast

from sqlalchemy import delete, select, update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.crud import AbstractCRUDRepository, CRUDFactory
from src.modules.event_groups.schemas import (
    CreateEventGroup,
    CreateEventGroupWithoutTags,
    UpdateEventGroup,
    ViewEventGroup,
)
from src.modules.ownership import OwnershipEnum, setup_ownership_method
from src.storages.sql import SQLAlchemyStorage
from src.storages.sql.models import EventGroup

CRUD: AbstractCRUDRepository[
    CreateEventGroupWithoutTags,
    ViewEventGroup,
    UpdateEventGroup,
] = CRUDFactory(
    EventGroup,
    CreateEventGroupWithoutTags,
    ViewEventGroup,
    UpdateEventGroup,
)


class SqlEventGroupRepository:
    storage: SQLAlchemyStorage

    def update_storage(self, storage: SQLAlchemyStorage):
        self.storage = storage

    def _create_session(self) -> AsyncSession:
        return self.storage.create_session()

    # ----------------- CRUD ----------------- #

    async def create(self, group: CreateEventGroup) -> ViewEventGroup:
        from src.modules.tags.repository import tag_repository

        tags_ids = []
        if group.tags:
            tags_ids = [tag.id for tag in await tag_repository.batch_create_or_read(group.tags)]

        async with self._create_session() as session:
            # without CRUD
            q = insert(EventGroup).values(group.model_dump(exclude={"tags"})).returning(EventGroup)
            obj = await session.scalar(q)
            if tags_ids:  # add tags
                q = (
                    insert(EventGroup.tags_association)
                    .values([{"object_id": obj.id, "tag_id": tag_id} for tag_id in tags_ids])
                    .on_conflict_do_nothing()
                )
                await session.execute(q)
            await session.commit()
            return ViewEventGroup.model_validate(group)

    async def batch_create(self, groups: list[CreateEventGroupWithoutTags]) -> list[ViewEventGroup]:
        if not groups:
            return []

        async with self._create_session() as session:
            return await CRUD.batch_create(session, groups)

    async def create_or_update(self, group: CreateEventGroup) -> int:
        from src.modules.tags.repository import tag_repository

        async with self._create_session() as session:
            insert_stmt = insert(EventGroup).values(group.model_dump(exclude={"tags"}))
            update_dict = {c.name: c for c in cast(Iterable, insert_stmt.excluded) if not c.primary_key}
            q = insert_stmt.on_conflict_do_update(index_elements=["alias"], set_=update_dict).returning(EventGroup.id)
            obj_id = await session.scalar(q)
            await session.commit()

            tags_ids = []
            if group.tags:
                tags_ids = [tag.id for tag in await tag_repository.batch_create_or_read(group.tags)]

            await tag_repository.set_tags_to_event_group(obj_id, tags_ids)
            return obj_id

    async def batch_create_or_read(self, groups: list[CreateEventGroup]) -> list[ViewEventGroup]:
        from src.modules.tags.repository import tag_repository

        async with self._create_session() as session:
            insert_stmt = insert(EventGroup).values([group.model_dump(exclude={"tags"}) for group in groups])
            update_dict = {c.name: c for c in cast(Iterable, insert_stmt.excluded) if not c.primary_key}

            q = insert_stmt.on_conflict_do_update(index_elements=["alias"], set_=update_dict).returning(EventGroup.id)
            obj_ids = (await session.scalars(q)).all()
            await session.commit()

        # set tags
        _create_tags = list(set(tag for group in groups for tag in group.tags))
        db_tags = await tag_repository.batch_create_or_read(_create_tags)
        alias_x_tag = {(tag.alias, tag.type): tag for tag in db_tags}
        event_group_id_x_tags_ids = dict()
        for group, group_id in zip(groups, obj_ids):
            tag_ids = [alias_x_tag[(tag.alias, tag.type)].id for tag in group.tags]
            event_group_id_x_tags_ids[group_id] = tag_ids
        await tag_repository.batch_set_tags_to_event_group(event_group_id_x_tags_ids)

        objs = await session.scalars(select(EventGroup).where(EventGroup.id.in_(obj_ids)))

        return [ViewEventGroup.model_validate(obj) for obj in objs]

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

    async def read_by_path(self, path: str) -> ViewEventGroup | None:
        async with self._create_session() as session:
            return await CRUD.read_by(session, only_first=True, path=path)

    async def read_by_alias(self, alias: str) -> ViewEventGroup | None:
        async with self._create_session() as session:
            return await CRUD.read_by(session, only_first=True, alias=alias)

    async def batch_read_ids_by_aliases(self, aliases: list[str]) -> dict[str, int | None]:
        async with self._create_session() as session:
            q = select(EventGroup.id, EventGroup.alias).where(EventGroup.alias.in_(aliases))
            rows = (await session.execute(q)).all()
            result = dict.fromkeys(aliases, None)
            for row in rows:
                result[row.alias] = row.id
            return result

    async def update(self, event_group_id: int, event_group: UpdateEventGroup) -> ViewEventGroup:
        async with self._create_session() as session:
            return await CRUD.update(session, data=event_group, id=event_group_id)

    async def batch_update(self, event_groups: dict[int, "UpdateEventGroup"]) -> list["ViewEventGroup"]:
        if not event_groups:
            return []
        async with self._create_session() as session:
            data = list(event_groups.values())

            return await CRUD.batch_update(
                session, data=data, pkeys=[{"id": event_group_id} for event_group_id in event_groups.keys()]
            )

    async def delete_by_alias(self, alias: str) -> None:
        async with self._create_session() as session:
            q = delete(EventGroup).where(EventGroup.alias == alias)
            await session.execute(q)
            await session.commit()

    # ^^^^^^^^^^^^^^^^^ CRUD ^^^^^^^^^^^^^^^^^ #

    async def setup_ownership(self, group_id: int, user_id: int, role_alias: "OwnershipEnum") -> None:
        async with self._create_session() as session:
            OwnershipClass = EventGroup.Ownership
            return await setup_ownership_method(OwnershipClass, session, group_id, user_id, role_alias)

    async def update_timestamp(self, group_id: int):
        async with self._create_session() as session:
            # updated_at
            q = update(EventGroup).where(EventGroup.id == group_id).values()
            await session.execute(q)
            await session.commit()


event_group_repository: SqlEventGroupRepository = SqlEventGroupRepository()
