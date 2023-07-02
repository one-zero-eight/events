__all__ = ["SqlUserRepository"]

from sqlalchemy import select, delete
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import selectinload

from src.app.event_groups.schemas import (
    ViewEventGroup,
    UserXGroupView,
)
from src.app.users.schemas import CreateUser, ViewUser
from src.repositories.users.abc import AbstractUserRepository, USER_ID
from src.storages.sql.models import User, EventGroup, UserXGroup, UserXFavorite
from src.storages.sql.storage import AbstractSQLAlchemyStorage
from src.exceptions import DBEventGroupDoesNotExistInDb


def SELECT_USER_BY_ID(id_: USER_ID):
    return (
        select(User)
        .where(User.id == id_)
        .options(
            selectinload(User.favorites_association),
            selectinload(User.groups_association),
        )
    )


class SqlUserRepository(AbstractUserRepository):
    storage: AbstractSQLAlchemyStorage

    def __init__(self, storage: AbstractSQLAlchemyStorage):
        self.storage = storage

    async def get_user(self, user_id: USER_ID) -> ViewUser:
        async with self.storage.create_session() as session:
            user = await session.scalar(SELECT_USER_BY_ID(user_id))
            if user:
                return ViewUser.from_orm(user)

    async def batch_get_user(self, ids: list[USER_ID]) -> list[ViewUser]:
        async with self.storage.create_session() as session:
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

    async def create_user_if_not_exists(self, user: CreateUser) -> ViewUser:
        async with self.storage.create_session() as session:
            q = insert(User).values(**user.dict())
            q = (
                q.on_conflict_do_update(
                    index_elements=[User.email], set_={"id": User.id}
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

    async def batch_create_user_if_not_exists(
        self, users: list[CreateUser]
    ) -> list[ViewUser]:
        async with self.storage.create_session() as session:
            q = insert(User).values([user.dict() for user in users])
            q = (
                q.on_conflict_do_update(
                    index_elements=[User.email], set_={"id": User.id}
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

    async def get_user_id_by_email(self, email: str) -> USER_ID:
        async with self.storage.create_session() as session:
            user_id = await session.scalar(select(User.id).where(User.email == email))
            return user_id

    async def add_favorite(
        self, user_id: USER_ID, favorite_id: int
    ) -> list[ViewEventGroup]:
        async with self.storage.create_session() as session:
            # check if favorite exists
            favorite = await session.scalar(
                select(EventGroup).where(EventGroup.id == favorite_id)
            )
            if not favorite:
                raise DBEventGroupDoesNotExistInDb(id=favorite_id)

            q = (
                insert(UserXFavorite)
                .values(
                    user_id=user_id,
                    group_id=favorite_id,
                )
                .on_conflict_do_nothing(
                    index_elements=[UserXFavorite.user_id, UserXFavorite.group_id]
                )
            )
            await session.execute(q)
            await session.commit()

            user = await session.scalar(SELECT_USER_BY_ID(user_id))

            return [
                UserXGroupView.from_orm(group) for group in user.favorites_association
            ]

    async def remove_favorite(
        self, user_id: USER_ID, favorite_id: int
    ) -> list[UserXGroupView]:
        async with self.storage.create_session() as session:
            # check if favorite exists and belongs to user, then remove
            q = (
                delete(UserXFavorite)
                .where(
                    UserXFavorite.user_id == user_id,
                )
                .where(
                    UserXFavorite.group_id == favorite_id,
                )
            )
            await session.execute(q)
            user = await session.scalar(SELECT_USER_BY_ID(user_id))
            await session.commit()
            # from association
            return [
                UserXGroupView.from_orm(group) for group in user.favorites_association
            ]
