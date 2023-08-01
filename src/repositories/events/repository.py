__all__ = ["SqlEventRepository"]

from sqlalchemy.dialects.postgresql import insert as postgres_insert
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from src.repositories.crud import CRUDFactory
from src.repositories.events.abc import AbstractEventRepository
from src.schemas import CreateEvent, UpdateEvent, ViewEvent, AddEventPatch, ViewEventPatch, UpdateEventPatch
from src.storages.sql import AbstractSQLAlchemyStorage
from src.storages.sql.models import Event, EventPatch

CRUD = CRUDFactory(
    Event,
    CreateEvent,
    ViewEvent,
    UpdateEvent,
    get_options=(selectinload(Event.patches),),
)


class SqlEventRepository(AbstractEventRepository):
    storage: AbstractSQLAlchemyStorage

    def __init__(self, storage: AbstractSQLAlchemyStorage):
        self.storage = storage

    def _create_session(self) -> AsyncSession:
        return self.storage.create_session()

    # ----------------- CRUD ----------------- #

    async def create(self, event: "CreateEvent") -> "ViewEvent":
        async with self._create_session() as session:
            db_event = Event(
                **event.dict(exclude={"patches"}), patches=[EventPatch(**patch.dict()) for patch in event.patches]
            )
            session.add(db_event)
            await session.commit()
            # update event
            await session.refresh(db_event)
            return ViewEvent.from_orm(db_event)

    async def read(self, event_id: int) -> "ViewEvent":
        async with self._create_session() as session:
            return await CRUD.read(session, id=event_id)

    async def update(self, event_id: int, event: "UpdateEvent") -> "ViewEvent":
        async with self._create_session() as session:
            return await CRUD.update(session, event, id=event_id)

    async def delete(self, event_id: int) -> None:
        async with self._create_session() as session:
            await CRUD.delete(session, id=event_id)

    # ^^^^^^^^^^^^^^^^^^ CRUD ^^^^^^^^^^^^^^^ #
    # ----------------- PATCHES ----------------- #
    async def add_patch(self, event_id: int, patch: "AddEventPatch") -> "ViewEventPatch":
        async with self._create_session() as session:
            q = (
                postgres_insert(EventPatch)
                .values(parent_id=event_id, **patch.dict())
                .returning(EventPatch)
                .options(joinedload(EventPatch.parent))
            )
            event_patch = await session.scalar(q)
            await session.commit()
            return ViewEventPatch.from_orm(event_patch)

    async def read_patches(self, event_id: int) -> list["ViewEventPatch"]:
        async with self._create_session() as session:
            q = select(EventPatch).where(EventPatch.parent_id == event_id).options(joinedload(EventPatch.parent))
            event_patches = await session.scalars(q)
            return [ViewEventPatch.from_orm(event_patch) for event_patch in event_patches]

    async def update_patch(self, patch_id: int, patch: "UpdateEventPatch") -> "ViewEventPatch":
        async with self._create_session() as session:
            q = (
                update(EventPatch)
                .where(EventPatch.id == patch_id)
                .values(**patch.dict(exclude_unset=True))
                .returning(EventPatch)
            )
            event_patch = await session.scalar(q)
            await session.commit()
            return ViewEventPatch.from_orm(event_patch)

    # ^^^^^^^^^^^^^^^^^^ PATCHES ^^^^^^^^^^^^^^^ #
