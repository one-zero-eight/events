__all__ = ["SqlTagRepository"]

from sqlalchemy import select, delete
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import selectinload

from src.repositories.tags.abc import AbstractTagRepository
from src.schemas import CreateTag, ViewTag, OwnershipEnum
from src.storages.sql import AbstractSQLAlchemyStorage
from src.storages.sql.models import Tag, TagOwnership, EventGroup


class SqlTagRepository(AbstractTagRepository):
    storage: AbstractSQLAlchemyStorage

    def __init__(self, storage: AbstractSQLAlchemyStorage):
        self.storage = storage

    async def get_tag(self, tag_id: int) -> "ViewTag":
        async with self.storage.create_session() as session:
            q = select(Tag).where(Tag.id == tag_id)
            tag = await session.scalar(q)
            if tag:
                return ViewTag.from_orm(tag)

    async def get_tags_by_ids(self, tag_ids: list[int]) -> list["ViewTag"]:
        async with self.storage.create_session() as session:
            q = select(Tag).where(Tag.id.in_(tag_ids))
            tags = await session.scalars(q)
            return [ViewTag.from_orm(tag) for tag in tags]

    async def get_all_tags(self) -> list["ViewTag"]:
        async with self.storage.create_session() as session:
            q = select(Tag).order_by(Tag.id)
            tags = await session.scalars(q)
            return [ViewTag.from_orm(tag) for tag in tags]

    async def get_tag_by_name(self, name: str) -> "ViewTag":
        async with self.storage.create_session() as session:
            q = select(Tag).where(Tag.name == name)
            tag = await session.scalar(q)
            return ViewTag.from_orm(tag)

    async def create_tag_if_not_exists(self, tag: "CreateTag") -> ViewTag:
        async with self.storage.create_session() as session:
            q = insert(Tag).values(**tag.dict()).returning(Tag)
            q = q.on_conflict_do_update(index_elements=[Tag.alias, Tag.type], set_={"id": Tag.id})

            tag = await session.scalar(q)
            await session.commit()
            return ViewTag.from_orm(tag)

    async def batch_create_tag_if_not_exists(self, tags: list["CreateTag"]) -> list[ViewTag]:
        async with self.storage.create_session() as session:
            q = (
                insert(Tag)
                .on_conflict_do_update(
                    index_elements=[Tag.alias, Tag.type],
                    set_={"id": Tag.id},
                )
                .values([tag.dict() for tag in tags])
                .options(
                    selectinload(Tag.ownership_association),
                )
                .returning(Tag)
            )

            tags = await session.scalars(q)
            await session.commit()
            return [ViewTag.from_orm(tag) for tag in tags]

    async def setup_ownership(self, tag_id: int, user_id: int, ownership_enum: OwnershipEnum) -> None:
        async with self.storage.create_session() as session:
            if ownership_enum is OwnershipEnum.default:
                # just delete row
                q = delete(TagOwnership).where(TagOwnership.user_id == user_id).where(TagOwnership.tag_id == tag_id)
                await session.execute(q)
            else:
                # insert or update
                q = insert(TagOwnership).values(
                    user_id=user_id,
                    tag_id=tag_id,
                    ownership_enum=ownership_enum.value,
                )
                q = q.on_conflict_do_update(
                    index_elements=[TagOwnership.user_id, TagOwnership.tag_id],
                    set_={"ownership_enum": ownership_enum.value},
                )
                await session.execute(q)
            await session.commit()

    async def add_tags_to_event_group(self, event_group_id: int, tag_ids: list[int]) -> None:
        async with self.storage.create_session() as session:
            table = EventGroup.__tags_mixin_table__
            q = (
                insert(table)
                .values([{"event_group_id": event_group_id, "tag_id": tag_id} for tag_id in tag_ids])
                .on_conflict_do_nothing()
            )
            await session.execute(q)
            await session.commit()

    async def batch_add_tags_to_event_group(self, tags_mapping: dict[int, list[int]]) -> None:
        async with self.storage.create_session() as session:
            table = EventGroup.__tags_mixin_table__
            q = (
                insert(table)
                .values(
                    [
                        {
                            "event_groups_id": event_group_id,
                            "tag_id": tag_id,
                        }
                        for event_group_id, tag_ids in tags_mapping.items()
                        for tag_id in tag_ids
                    ]
                )
                .on_conflict_do_nothing()
            )
            await session.execute(q)
            await session.commit()

    async def remove_tags_from_event_group(self, event_group_id: int, tag_ids: list[int]) -> None:
        async with self.storage.create_session() as session:
            table = EventGroup.__tags_mixin_table__
            q = delete(table).where(table.c.event_group_id == event_group_id).where(table.c.tag_id.in_(tag_ids))
            await session.execute(q)
            await session.commit()
