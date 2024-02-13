__all__ = ["SqlUserRepository"]

import random
import string
from typing import Literal

from sqlalchemy import select, delete, update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy.sql.expression import exists

from src.exceptions import DBEventGroupDoesNotExistInDb
from src.repositories.crud import CRUDFactory, AbstractCRUDRepository
from src.schemas import LinkedCalendarView
from src.schemas.linked import LinkedCalendarCreate
from src.schemas.users import CreateUser, ViewUser, UpdateUser, ViewUserScheduleKey
from src.storages.sql.models import User, EventGroup, UserXFavoriteEventGroup, LinkedCalendar, UserScheduleKeys
from src.storages.sql.storage import SQLAlchemyStorage

_get_options = (
    selectinload(User.favorites_association),
    selectinload(User.linked_calendars),
)


def SELECT_USER_BY_ID(id_: int):
    return select(User).where(User.id == id_).options(*_get_options)


CRUD: AbstractCRUDRepository[
    CreateUser,
    ViewUser,
    UpdateUser,
] = CRUDFactory(User, CreateUser, ViewUser, UpdateUser, get_options=_get_options)

MIN_USER_ID = 100_000
MAX_USER_ID = 999_999


async def _get_available_user_ids(session: AsyncSession, count: int = 1) -> list[int] | int:
    q = select(User.id)
    excluded_ids = set(await session.scalars(q))
    excluded_ids: set[int]
    available_ids = set()
    while len(available_ids) < count:
        chosen_id = random.randint(MIN_USER_ID, MAX_USER_ID)
        if chosen_id not in excluded_ids:
            available_ids.add(chosen_id)
    return list(available_ids) if count > 1 else available_ids.pop()


def _generate_random_user_schedule_key() -> str:
    return "".join(random.choices(string.ascii_letters, k=6))


class SqlUserRepository:
    storage: SQLAlchemyStorage

    def __init__(self, storage: SQLAlchemyStorage):
        self.storage = storage

    def _create_session(self) -> AsyncSession:
        return self.storage.create_session()

    # ------------------ CRUD ------------------ #
    async def create_or_read(self, user: CreateUser) -> ViewUser:
        async with self._create_session() as session:
            user.id = await _get_available_user_ids(session)
            created = await CRUD.create_if_not_exists(session, user)
            if created is None:
                created = await CRUD.read_by(session, only_first=True, email=user.email)
            return created

    async def batch_create_or_read(self, users: list[CreateUser]) -> list[ViewUser]:
        async with self._create_session() as session:
            available_ids = await _get_available_user_ids(session, len(users))
            for user, id_ in zip(users, available_ids):
                user.id = id_
            q = insert(User).values([user.dict() for user in users])
            q = (
                q.on_conflict_do_update(index_elements=[User.email], set_={"id": User.id})
                .returning(User)
                .options(*_get_options)
            )
            db_users = await session.scalars(q)
            await session.commit()
            return [ViewUser.model_validate(user) for user in db_users]

    async def create_or_update(self, user: CreateUser) -> ViewUser:
        async with self._create_session() as session:
            user.id = await _get_available_user_ids(session)
            q = insert(User).values(**user.dict())
            q = (
                q.on_conflict_do_update(index_elements=[User.email], set_={**q.excluded, "id": User.id})
                .returning(User)
                .options(*_get_options)
            )
            user = await session.scalar(q)
            await session.commit()
            return ViewUser.model_validate(user)

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
            return ViewUser.model_validate(user)

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
            return ViewUser.model_validate(user)

    async def set_hidden_event_group(self, user_id: int, group_id: int, hide: bool = True) -> "ViewUser":
        async with self._create_session() as session:
            # find favorite where user_id and group_id
            q = (
                select(UserXFavoriteEventGroup)
                .where(UserXFavoriteEventGroup.user_id == user_id)
                .where(UserXFavoriteEventGroup.group_id == group_id)
            )

            event_group = await session.scalar(q)

            # set hidden
            if event_group:
                event_group.hidden = hide

            # from table
            q = select(User).where(User.id == user_id).options(*_get_options)
            user = await session.scalar(q)
            await session.commit()
            return ViewUser.model_validate(user)

    async def set_hidden(self, user_id: int, target: Literal["music-room", "sports", "moodle"], hide: bool = True):
        async with self._create_session() as session:
            q = (
                update(User)
                .where(User.id == user_id)
                .values(
                    {
                        "music_room_hidden": hide if target == "music-room" else User.music_room_hidden,
                        "sports_hidden": hide if target == "sports" else User.sports_hidden,
                        "moodle_hidden": hide if target == "moodle" else User.moodle_hidden,
                    }
                )
                .returning(User)
                .options(*_get_options)
            )
            user = await session.scalar(q)
            await session.commit()
            return ViewUser.model_validate(user)

    async def link_calendar(self, user_id: int, calendar: "LinkedCalendarCreate") -> "LinkedCalendarView":
        async with self._create_session() as session:
            q = (
                insert(LinkedCalendar)
                .values(
                    user_id=user_id,
                    **calendar.dict(),
                )
                .returning(LinkedCalendar)
            )

            calendar = await session.scalar(q)
            await session.commit()
            return LinkedCalendarView.model_validate(calendar)

    async def generate_user_schedule_key(self, user_id: int, resource_path: str) -> ViewUserScheduleKey:
        async with self._create_session() as session:
            key = _generate_random_user_schedule_key()
            q = insert(UserScheduleKeys).values(
                user_id=user_id,
                access_key=key,
                resource_path=resource_path,
            )
            await session.execute(q)
            await session.commit()
            return ViewUserScheduleKey(access_key=key, resource_path=resource_path, user_id=user_id)

    async def get_user_schedule_keys(self, user_id: int) -> list[ViewUserScheduleKey]:
        async with self._create_session() as session:
            q = select(UserScheduleKeys).where(UserScheduleKeys.user_id == user_id)
            keys = await session.scalars(q)
            return [ViewUserScheduleKey.model_validate(key, from_attributes=True) for key in keys]

    async def get_user_schedule_key_for_resource(self, user_id: int, resource_path: str) -> ViewUserScheduleKey | None:
        async with self._create_session() as session:
            q = select(UserScheduleKeys).where(
                UserScheduleKeys.user_id == user_id,
                UserScheduleKeys.resource_path == resource_path,
            )
            key = await session.scalar(q)
            return ViewUserScheduleKey.model_validate(key, from_attributes=True) if key else None

    async def check_user_schedule_key(self, user_id: int, key: str, resource_path: str) -> bool:
        async with self._create_session() as session:
            q = select(UserScheduleKeys).where(
                UserScheduleKeys.user_id == user_id,
                UserScheduleKeys.access_key == key,
                UserScheduleKeys.resource_path == resource_path,
            )
            keyring = await session.scalar(q)
            return keyring is not None

    async def delete_user_schedule_key(self, user_id: int, key: str, resource_path: str) -> None:
        async with self._create_session() as session:
            q = delete(UserScheduleKeys).where(
                UserScheduleKeys.user_id == user_id,
                UserScheduleKeys.access_key == key,
                UserScheduleKeys.resource_path == resource_path,
            )
            await session.execute(q)
            await session.commit()
