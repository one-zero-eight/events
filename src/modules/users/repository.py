__all__ = ["SqlUserRepository", "user_repository"]

import random
import string
from typing import Literal

from sqlalchemy import delete, select, update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy.sql.expression import exists

from src.exceptions import EventGroupNotFoundException
from src.modules.crud import AbstractCRUDRepository, CRUDFactory
from src.modules.users.linked import LinkedCalendarCreate, LinkedCalendarView
from src.modules.users.schemas import CreateUser, UpdateUser, ViewUser, ViewUserScheduleKey
from src.storages.sql.models import EventGroup, LinkedCalendar, User, UserScheduleKeys, UserXFavoriteEventGroup
from src.storages.sql.models.event_groups import UserXHiddenEventGroup
from src.storages.sql.storage import SQLAlchemyStorage

_get_options = (
    selectinload(User.favorites_association),
    selectinload(User.linked_calendars),
    selectinload(User.hidden_event_groups_association),
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

    def update_storage(self, storage: SQLAlchemyStorage):
        self.storage = storage

    def _create_session(self) -> AsyncSession:
        return self.storage.create_session()

    async def create(self, user: CreateUser) -> ViewUser:
        async with self._create_session() as session:
            user.id = await _get_available_user_ids(session)
            created = await CRUD.create(session, user)
            return created

    async def read(self, user_id: int) -> ViewUser:
        async with self._create_session() as session:
            return await CRUD.read(session, id=user_id)

    async def read_all(self) -> list[ViewUser]:
        async with self._create_session() as session:
            return await CRUD.read_all(session)

    async def read_mapping_by_emails(self, emails: list[str]) -> dict[str, int | None]:
        async with self._create_session() as session:
            q = select(User.email, User.id).where(User.email.in_(emails))
            mapping = (await session.execute(q)).all()
            result = dict.fromkeys(emails)
            for email, user_id in mapping:
                result[email] = user_id
            return result

    async def read_id_by_email(self, email: str) -> int:
        async with self._create_session() as session:
            user_id = await session.scalar(select(User.id).where(User.email == email))
            return user_id

    async def read_id_by_innohassle_id(self, innohassle_id: str) -> int | None:
        async with self._create_session() as session:
            user_id = await session.scalar(select(User.id).where(User.innohassle_id == innohassle_id))
            return user_id

    async def update_innohassle_id(self, user_id: int, innohassle_id: str) -> None:
        async with self._create_session() as session:
            q = update(User).where(User.id == user_id).values(innohassle_id=innohassle_id)
            await session.execute(q)
            await session.commit()

    async def add_favorite(self, user_id: int, favorite_id: int) -> ViewUser:
        async with self._create_session() as session:
            # check if favorite exists
            favorite_exists = await session.scalar(exists(EventGroup.id).where(EventGroup.id == favorite_id).select())

            if not favorite_exists:
                raise EventGroupNotFoundException(detail=f"Event group with id {favorite_id} does not exist")

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
            )
            await session.execute(q)
            user = await session.scalar(SELECT_USER_BY_ID(user_id))
            await session.commit()
            return ViewUser.model_validate(user)

    async def set_hidden_event_group(self, user_id: int, group_id: int, hide: bool = True) -> "ViewUser":
        async with self._create_session() as session:
            if hide:
                q = (
                    insert(UserXHiddenEventGroup)
                    .values(
                        user_id=user_id,
                        group_id=group_id,
                    )
                    .on_conflict_do_nothing(
                        index_elements=[UserXHiddenEventGroup.user_id, UserXHiddenEventGroup.group_id]
                    )
                )
            else:
                q = delete(UserXHiddenEventGroup).where(
                    UserXHiddenEventGroup.user_id == user_id,
                    UserXHiddenEventGroup.group_id == group_id,
                )
            await session.execute(q)
            await session.commit()
            # from table
            q = select(User).where(User.id == user_id).options(*_get_options)
            user = await session.scalar(q)
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
                    **calendar.model_dump(),
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

    async def set_user_moodle_data(self, user_id: int, moodle_userid: int, moodle_calendar_authtoken: str) -> None:
        async with self._create_session() as session:
            q = (
                update(User)
                .where(User.id == user_id)
                .values(
                    {
                        "moodle_userid": moodle_userid,
                        "moodle_calendar_authtoken": moodle_calendar_authtoken,
                    }
                )
            )
            await session.execute(q)
            await session.commit()


user_repository: SqlUserRepository = SqlUserRepository()
