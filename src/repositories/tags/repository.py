__all__ = ["SqlTagRepository"]

from sqlalchemy import delete
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.repositories.crud import CRUDFactory
from src.repositories.tags.abc import AbstractTagRepository
from src.schemas import CreateTag, ViewTag, OwnershipEnum, UpdateTag
from src.storages.sql import AbstractSQLAlchemyStorage
from src.storages.sql.models import Tag, EventGroup

CRUD = CRUDFactory(Tag, CreateTag, ViewTag, UpdateTag)


class SqlTagRepository(AbstractTagRepository):
    storage: AbstractSQLAlchemyStorage

    def __init__(self, storage: AbstractSQLAlchemyStorage):
        self.storage = storage

    def _create_session(self) -> AsyncSession:
        return self.storage.create_session()

    # ------------------ CRUD ------------------ #
    async def create_or_read(self, tag: "CreateTag") -> ViewTag:
        async with self._create_session() as session:
            created = await CRUD.create_if_not_exists(session, tag)
            if created is None:
                created = await CRUD.read_by(session, only_first=True, alias=tag.alias, type=tag.type)
            return created

    async def batch_create_or_read(self, tags: list["CreateTag"]) -> list[ViewTag]:
        async with self._create_session() as session:
            q = (
                insert(Tag)
                .on_conflict_do_update(
                    index_elements=[Tag.alias, Tag.type],
                    set_={"id": Tag.id},
                )
                .values([tag.dict() for tag in tags])
                .options(
                    selectinload(Tag.ownerships),
                )
                .returning(Tag)
            )

            tags = await session.scalars(q)
            await session.commit()
            return [ViewTag.from_orm(tag) for tag in tags]

    async def read(self, id: int) -> "ViewTag":
        async with self._create_session() as session:
            return await CRUD.read(session, id=id)

    async def read_all(self) -> list["ViewTag"]:
        async with self._create_session() as session:
            return await CRUD.read_all(session)

    async def batch_read(self, tag_ids: list[int]) -> list["ViewTag"]:
        async with self._create_session() as session:
            return await CRUD.batch_read(session, pkeys=[{"id": tag_id} for tag_id in tag_ids])

    async def read_by_name(self, name: str) -> "ViewTag":
        async with self._create_session() as session:
            return await CRUD.read_by(session, only_first=True, name=name)

    async def update(self, id: int, tag: "UpdateTag") -> "ViewTag":
        async with self._create_session() as session:
            return await CRUD.update(session, data=tag, id=id)

    async def delete(self, id: int) -> None:
        async with self._create_session() as session:
            await CRUD.delete(session, id=id)

    # ^^^^^^^^^^^^^^^^^^^^ CRUD ^^^^^^^^^^^^^^^^^^^^ #

    async def setup_ownership(self, tag_id: int, user_id: int, role_alias: OwnershipEnum) -> None:
        async with self._create_session() as session:
            TagOwnership = Tag.Ownership

            if role_alias is OwnershipEnum.default:
                # just delete row
                q = delete(TagOwnership).where(TagOwnership.user_id == user_id).where(TagOwnership.object_id == tag_id)
                await session.execute(q)
            else:
                # insert or update
                q = insert(TagOwnership).values(
                    user_id=user_id,
                    object_id=tag_id,
                    role_alias=role_alias,
                )
                q = q.on_conflict_do_update(
                    index_elements=[TagOwnership.user_id, TagOwnership.object_id],
                    set_={"role_alias": role_alias.value},
                )
                await session.execute(q)
            await session.commit()

    async def add_tags_to_event_group(self, event_group_id: int, tag_ids: list[int]) -> None:
        async with self._create_session() as session:
            table = Tag.__tags_associations__[EventGroup.__tablename__]
            q = (
                insert(table)
                .values([{"object_id": event_group_id, "tag_id": tag_id} for tag_id in tag_ids])
                .on_conflict_do_nothing()
            )
            await session.execute(q)
            await session.commit()

    async def batch_add_tags_to_event_group(self, tags_mapping: dict[int, list[int]]) -> None:
        async with self._create_session() as session:
            table = Tag.__tags_associations__[EventGroup.__tablename__]

            values = [
                {
                    "object_id": event_group_id,
                    "tag_id": tag_id,
                }
                for event_group_id, tag_ids in tags_mapping.items()
                for tag_id in tag_ids
                if tag_ids
            ]
            if values:
                q = insert(table).values(values).on_conflict_do_nothing()
                await session.execute(q)
                await session.commit()

    async def remove_tags_from_event_group(self, event_group_id: int, tag_ids: list[int]) -> None:
        async with self._create_session() as session:
            table = Tag.__tags_associations__[EventGroup.__tablename__]
            q = delete(table).where(table.object_id == event_group_id).where(table.tag_id.in_(tag_ids))
            await session.execute(q)
            await session.commit()
