__all__ = ["SqlUserRepository"]

from sqlalchemy import select, delete
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy.sql.expression import exists

from src.exceptions import DBEventGroupDoesNotExistInDb
from src.repositories.crud import CRUDFactory
from src.repositories.users.abc import AbstractUserRepository
from src.schemas.users import CreateUser, ViewUser, UpdateUser
from src.storages.sql.models import User, EventGroup, UserXFavoriteEventGroup
from src.storages.sql.storage import AbstractSQLAlchemyStorage


def SELECT_USER_BY_ID(id_: int):
    return (
        select(User)
        .where(User.id == id_)
        .options(
            selectinload(User.favorites_association),
        )
    )


CRUD = CRUDFactory(User, CreateUser, ViewUser, UpdateUser, get_options=(selectinload(User.favorites_association),))


class SqlUserRepository(AbstractUserRepository):
    storage: AbstractSQLAlchemyStorage

    def __init__(self, storage: AbstractSQLAlchemyStorage):
        self.storage = storage

    def _create_session(self) -> AsyncSession:
        return self.storage.create_session()

    # ------------------ CRUD ------------------ #
    async def create_or_read(self, user: CreateUser) -> ViewUser:
        async with self._create_session() as session:
            created = await CRUD.create_if_not_exists(session, user)
            if created is None:
                created = await CRUD.read_by(session, only_first=True, email=user.email)
            return created

    async def batch_create_or_read(self, users: list[CreateUser]) -> list[ViewUser]:
        async with self._create_session() as session:
            q = insert(User).values([user.dict() for user in users])
            q = (
                q.on_conflict_do_update(index_elements=[User.email], set_={"id": User.id})
                .returning(User)
                .options(
                    selectinload(User.favorites_association),
                )
            )
            db_users = await session.scalars(q)
            await session.commit()
            return [ViewUser.from_orm(user) for user in db_users]

    async def create_or_update(self, user: CreateUser) -> ViewUser:
        async with self._create_session() as session:
            q = insert(User).values(**user.dict())
            q = (
                q.on_conflict_do_update(index_elements=[User.email], set_={**q.excluded, "id": User.id})
                .returning(User)
                .options(
                    selectinload(User.favorites_association),
                )
            )
            user = await session.scalar(q)
            await session.commit()
            return ViewUser.from_orm(user)

    async def read(self, user_id: int) -> ViewUser:
        async with self._create_session() as session:
            return await CRUD.read(session, id=user_id)

    async def read_id_by_email(self, email: str) -> int:
        async with self._create_session() as session:
            user_id = await session.scalar(select(User.id).where(User.email == email))
            return user_id

    async def batch_read(self, ids: list[int]) -> list[ViewUser]:
        async with self._create_session() as session:
            return await CRUD.batch_read(session, pkeys=[{"id": id_} for id_ in ids])

    # ^^^^^^^^^^^^^^^^^^^ CRUD ^^^^^^^^^^^^^^^^^^^ #

    async def add_favorite(self, user_id: int, favorite_id: int) -> ViewUser:
        async with self._create_session() as session:
            # check if favorite exists
            favorite_exists = await session.scalar(exists(EventGroup.id).where(EventGroup.id == favorite_id).select())

            if not favorite_exists:
                raise DBEventGroupDoesNotExistInDb(id=favorite_id)

            q = (
                insert(UserXFavoriteEventGroup)
                .values(
                    user_id=user_id,
                    group_id=favorite_id,
                )
                .on_conflict_do_nothing(
                    index_elements=[UserXFavoriteEventGroup.user_id, UserXFavoriteEventGroup.group_id]
                )
            )
            await session.execute(q)
            user = await session.scalar(SELECT_USER_BY_ID(user_id))
            await session.commit()
            return ViewUser.from_orm(user)

    async def remove_favorite(self, user_id: int, favorite_id: int) -> ViewUser:
        async with self._create_session() as session:
            q = (
                delete(UserXFavoriteEventGroup)
                .where(
                    UserXFavoriteEventGroup.user_id == user_id,
                )
                .where(
                    UserXFavoriteEventGroup.group_id == favorite_id,
                )
                .where(UserXFavoriteEventGroup.predefined.is_(False))
            )
            await session.execute(q)
            user = await session.scalar(SELECT_USER_BY_ID(user_id))
            await session.commit()
            return ViewUser.from_orm(user)
