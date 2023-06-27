__all__ = ["SqlUserRepository"]

from sqlalchemy import select, update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import selectinload

from src.app.event_groups.schemas import (
    CreateEventGroup,
    ViewEventGroup,
    UserXGroupView,
)
from src.app.users.schemas import CreateUser, ViewUser
from src.repositories.users.abc import AbstractUserRepository
from src.storages.sql.models import User, EventGroup, UserXGroup, UserXFavorite
from src.storages.sql.storage import AbstractSQLAlchemyStorage


def SELECT_USER_BY_EMAIL(email: str):
    return (
        select(User)
        .where(User.email == email)
        .options(
            selectinload(User.favorites_association),
            selectinload(User.groups_association),
        )
    )


class SqlUserRepository(AbstractUserRepository):
    storage: AbstractSQLAlchemyStorage

    def __init__(self, storage: AbstractSQLAlchemyStorage):
        self.storage = storage

    async def create_user_if_not_exists(self, user: CreateUser) -> ViewUser:
        async with self.storage.create_session() as session:
            q = insert(User).values(**user.dict())
            q = q.on_conflict_do_nothing(index_elements=[User.email])
            await session.execute(q)
            await session.commit()
        return await self.get_user_by_email(user.email)

    async def upsert_user(self, user: CreateUser) -> ViewUser:
        async with self.storage.create_session() as session:
            q = insert(User).values(**user.dict())
            q = (
                q.on_conflict_do_update(
                    index_elements=[User.email], set_={**q.excluded, "id": User.id}
                )
                .returning(User)
                .options(
                    selectinload(User.favorites_association),
                    selectinload(User.groups_association),
                )
            )
            user = await session.scalar(q)
            await session.commit()
            return ViewUser.from_orm(user)

    async def batch_upsert_users(self, users: list[CreateUser]) -> list[ViewUser]:
        async with self.storage.create_session() as session:
            q = insert(User).values([user.dict() for user in users])
            q = (
                q.on_conflict_do_update(
                    index_elements=[User.email], set_={**q.excluded, "id": User.id}
                )
                .returning(User)
                .options(
                    selectinload(User.favorites_association),
                    selectinload(User.groups_association),
                )
            )
            db_users = await session.scalars(q)
            await session.commit()
            return [ViewUser.from_orm(user) for user in db_users]

    async def get_user_by_email(self, email: str) -> ViewUser:
        async with self.storage.create_session() as session:
            q = SELECT_USER_BY_EMAIL(email)
            r = await session.scalar(q)
            return ViewUser.from_orm(r)

    async def batch_get_user(self, ids: list[int]) -> list[ViewUser]:
        async with self.storage.create_session() as session:
            # id is primary key, so we can use get
            q = (
                select(User)
                .where(User.id.in_(ids))
                .options(
                    selectinload(User.favorites_association),
                    selectinload(User.groups_association),
                )
            )
            r = await session.execute(q)
            return [ViewUser.from_orm(user) for user in r.scalars().all()]

    async def setup_groups(self, user_id: int, groups: list[int]):
        async with self.storage.create_session() as session:
            q = (
                select(User)
                .options(selectinload(User.groups_association))
                .where(User.id == user_id)
            )

            user = await session.scalar(q)
            user: User

            group_objs = await session.execute(
                select(EventGroup).where(EventGroup.id.in_(groups))
            )

            group_scalars = group_objs.scalars().all()
            user.groups = group_scalars
            await session.commit()

    async def batch_setup_groups(self, groups_mapping: dict[int, list[int]]):
        async with self.storage.create_session() as session:
            # in one query
            q = insert(UserXGroup).values(
                [
                    {"user_id": user_id, "group_id": group_id}
                    for user_id, group_ids in groups_mapping.items()
                    for group_id in group_ids
                ]
            )
            q = q.on_conflict_do_nothing(
                index_elements=[UserXGroup.user_id, UserXGroup.group_id]
            )
            await session.execute(q)
            await session.commit()

    async def add_favorite(
        self, email: str, favorite: CreateEventGroup
    ) -> list[ViewEventGroup]:
        async with self.storage.create_session() as session:
            # select user
            user = await session.scalar(SELECT_USER_BY_EMAIL(email))
            user: User
            # select favorite
            q = select(EventGroup).where(
                EventGroup.name == favorite.name and EventGroup.type == favorite.type
            )
            favorite_group = await session.scalar(q)
            if not favorite_group:
                favorite_group = EventGroup(**favorite.dict())
                session.add(favorite_group)
            # add favorite
            if favorite_group not in user.favorites:
                user.favorites.append(favorite_group)
            await session.commit()
            return [
                UserXGroupView.from_orm(group) for group in user.favorites_association
            ]

    async def remove_favorite(
        self, email: str, favorite: CreateEventGroup
    ) -> list[UserXGroupView]:
        async with self.storage.create_session() as session:
            # select user
            user = await session.scalar(SELECT_USER_BY_EMAIL(email))
            user: User
            # select favorite
            q = select(EventGroup).where(
                EventGroup.name == favorite.name and EventGroup.type == favorite.type
            )
            favorite_group = await session.scalar(q)
            if favorite_group and favorite_group in user.favorites:
                user.favorites.remove(favorite_group)
            await session.commit()
            # from association
            return [
                UserXGroupView.from_orm(group) for group in user.favorites_association
            ]

    async def set_hidden(
        self, user_id: int, is_favorite: bool, group_id: int, hidden: bool = True
    ):
        async with self.storage.create_session() as session:
            table = UserXFavorite if is_favorite else UserXGroup
            table: UserXFavorite | UserXGroup

            query = (
                update(table)
                .where(table.user_id == user_id)
                .where(table.group_id == group_id)
                .values(hidden=hidden)
            )
            await session.execute(query)
            await session.commit()

    async def upsert_group(self, group: CreateEventGroup) -> ViewEventGroup:
        async with self.storage.create_session() as session:
            q = insert(EventGroup).values(**group.dict()).returning(EventGroup)
            q = q.on_conflict_do_update(
                index_elements=[EventGroup.name],
                set_={**q.excluded, "id": EventGroup.id},
            )
            group = await session.scalar(q)
            await session.commit()
            return ViewEventGroup.from_orm(group)

    async def batch_upsert_groups(
        self, groups: list[CreateEventGroup]
    ) -> list[ViewEventGroup]:
        async with self.storage.create_session() as session:
            q = (
                insert(EventGroup)
                .values([group.dict() for group in groups])
                .returning(EventGroup)
            )
            q = q.on_conflict_do_update(
                index_elements=[EventGroup.name],
                set_={**q.excluded, "id": EventGroup.id},
            )
            db_groups = await session.scalars(q)
            await session.commit()
            return [ViewEventGroup.from_orm(group) for group in db_groups]
