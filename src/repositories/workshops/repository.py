__all__ = ["SqlWorkshopRepository"]

from sqlalchemy import delete
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.repositories.workshops.abc import AbstractWorkshopRepository
from src.schemas import CreateWorkshop, ViewWorkshop
from src.storages.sql import AbstractSQLAlchemyStorage
from src.storages.sql.models import Workshop, Timeslot


class SqlWorkshopRepository(AbstractWorkshopRepository):
    storage: AbstractSQLAlchemyStorage

    def __init__(self, storage: AbstractSQLAlchemyStorage):
        self.storage = storage

    def _create_session(self) -> AsyncSession:
        return self.storage.create_session()

    # ------------------ CRUD ------------------ #
    async def create_or_update(self, workshop: "CreateWorkshop") -> "ViewWorkshop":
        async with self._create_session() as session:
            q = insert(Workshop).values(
                workshop.dict(
                    exclude_none=True,
                    exclude={"timeslots"},
                )
            )
            set_ = {
                "id": Workshop.id,
                **q.excluded,
            }
            q = (
                q.on_conflict_do_update(index_elements=[Workshop.alias], set_=set_)
                .returning(Workshop)
                .options(selectinload(Workshop.timeslots))
            )
            db_workshop = await session.scalar(q)

            if workshop.timeslots is not None:
                await session.execute(delete(Timeslot).where(Timeslot.workshop_id == db_workshop.id))

                q = insert(Timeslot).values(
                    [
                        {
                            "workshop_id": db_workshop.id,
                            **timeslot.dict(exclude_none=True),
                        }
                        for timeslot in workshop.timeslots
                    ]
                )
                await session.execute(q)

            await session.commit()
            await session.refresh(db_workshop)
            return ViewWorkshop.from_orm(db_workshop)

    async def read(self, id: int) -> "ViewWorkshop":
        pass

    async def read_all(self) -> list["ViewWorkshop"]:
        pass

    async def read_by_alias(self, alias: str) -> "ViewWorkshop":
        pass

    # ^^^^^^^^^^^^^^^^^^^ CRUD ^^^^^^^^^^^^^^^^^^^ #
