__all__ = ["AbstractCRUDRepository", "CRUDFactory"]

from abc import abstractmethod, ABCMeta
from typing import Type, TypeVar, Generic

from pydantic import BaseModel as PydanticModel
from sqlalchemy import or_, and_, ColumnElement
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.base import ExecutableOption

from src.storages.sql.models.base import Base

# Define generic types
ViewType = TypeVar("ViewType", bound=PydanticModel)
CreateType = TypeVar("CreateType", bound=PydanticModel)
UpdateType = TypeVar("UpdateType", bound=PydanticModel)


class AbstractCRUDRepository(Generic[CreateType, ViewType, UpdateType], metaclass=ABCMeta):
    @abstractmethod
    async def create(self, session: AsyncSession, data: CreateType) -> ViewType:
        ...

    @abstractmethod
    async def create_if_not_exists(self, session: AsyncSession, data: CreateType) -> ViewType | None:
        ...

    @abstractmethod
    async def batch_create(self, session: AsyncSession, data: list[CreateType]) -> list[ViewType]:
        ...

    @abstractmethod
    async def read(self, session: AsyncSession, **pkeys) -> ViewType | None:
        ...

    @abstractmethod
    async def batch_read(self, session: AsyncSession, pkeys: list[dict[str, ...]]) -> list[ViewType]:
        ...

    @abstractmethod
    async def read_all(self, session: AsyncSession) -> list[ViewType]:
        ...

    @abstractmethod
    async def read_by(self, session: AsyncSession, only_first: bool, **columns) -> list[ViewType] | ViewType | None:
        ...

    @abstractmethod
    async def update(self, session: AsyncSession, data: UpdateType, **pkeys) -> ViewType:
        ...

    @abstractmethod
    async def batch_update(
        self, session: AsyncSession, data: list[UpdateType], pkeys: list[dict[str, ...]]
    ) -> list[ViewType]:
        ...

    @abstractmethod
    async def delete(self, session: AsyncSession, **pkeys) -> None:
        ...


# define generic type
ModelType = TypeVar("ModelType", bound=Base)


def CRUDFactory(
    Model: Type[ModelType],
    CreateScheme: Type[CreateType],
    ViewScheme: Type[ViewType],
    UpdateScheme: Type[UpdateType] = None,
    get_options: tuple[ExecutableOption, ...] = (),
) -> AbstractCRUDRepository[CreateType, ViewType, UpdateType]:
    from sqlalchemy import delete, insert, select, update as sql_update
    from sqlalchemy.dialects.postgresql import insert as postgres_insert
    from sqlalchemy.inspection import inspect

    table = Model.__table__
    primary_keys = [column.name for column in inspect(table).primary_key]

    def pkey_clause(pkeys: dict[str, int]) -> ColumnElement["bool"]:
        return and_(*[getattr(Model, pk) == pkeys[pk] for pk in primary_keys])

    class CRUD(AbstractCRUDRepository[CreateScheme, ViewScheme, UpdateScheme], metaclass=ABCMeta):
        # ------------------ CREATE -------------- #
        async def create(self, session: AsyncSession, data: CreateScheme) -> ViewScheme:
            _insert_query = insert(Model).returning(Model)
            if get_options:
                _insert_query = _insert_query.options(*get_options)
            obj = await session.scalar(_insert_query, params=data.dict())
            await session.commit()
            return ViewScheme.from_orm(obj)

        async def create_if_not_exists(self, session: AsyncSession, data: CreateScheme) -> ViewScheme | None:
            q = postgres_insert(Model).values(**data.dict()).on_conflict_do_nothing().returning(Model)
            if get_options:
                q = q.options(*get_options)
            obj = await session.scalar(q)
            await session.commit()
            if obj:
                return ViewScheme.from_orm(obj)

        async def batch_create(self, session: AsyncSession, data: list[CreateScheme]) -> list[ViewScheme]:
            if not data:
                return []
            _insert_query = insert(Model).returning(Model)
            if get_options:
                _insert_query = _insert_query.options(*get_options)
            objs = await session.scalars(_insert_query, params=[obj.dict() for obj in data])
            await session.commit()
            return [ViewScheme.from_orm(obj) for obj in objs]

        # ^^^^^^^^^^^^^^^^^^ CREATE ^^^^^^^^^^^^^^ #
        # ------------------ READ ---------------- #
        async def read(self, session: AsyncSession, **pkeys) -> ViewScheme:
            q = select(Model).where(pkey_clause(pkeys))
            if get_options:
                q = q.options(*get_options)
            obj = await session.scalar(q)
            if obj:
                return ViewScheme.from_orm(obj)

        async def batch_read(self, session: AsyncSession, pkeys: list[dict[str, ...]]) -> list[ViewScheme]:
            if not pkeys:
                return []

            q = select(Model).where(
                or_(
                    *[pkey_clause(pkey) for pkey in pkeys],
                )
            )

            if get_options:
                q = q.options(*get_options)
            objs = await session.scalars(q)

            return [ViewScheme.from_orm(obj) for obj in objs]

        async def read_all(self, session: AsyncSession) -> list[ViewScheme]:
            q = select(Model)
            if get_options:
                q = q.options(*get_options)
            objs = await session.scalars(q)
            return [ViewScheme.from_orm(obj) for obj in objs]

        async def read_by(
            self, session: AsyncSession, only_first: bool, **columns
        ) -> list[ViewScheme] | ViewScheme | None:
            q = select(Model).where(*[getattr(Model, column) == value for column, value in columns.items()])
            if get_options:
                q = q.options(*get_options)
            if only_first:
                obj = await session.scalar(q)
                return ViewScheme.from_orm(obj) if obj else None
            else:
                objs = await session.scalars(q)
                return [ViewScheme.from_orm(obj) for obj in objs]

        # ^^^^^^^^^^^^^^^^^^ READ ^^^^^^^^^^^^^^^^^^^ #
        async def update(self, session: AsyncSession, data: UpdateScheme, **pkeys) -> ViewScheme:
            q = sql_update(Model).values(**pkeys, **data.dict(exclude_unset=True)).returning(Model)
            if get_options:
                q = q.options(*get_options)
            obj = await session.scalar(q)
            await session.commit()
            return ViewScheme.from_orm(obj)

        async def batch_update(
            self, session: AsyncSession, data: list[UpdateScheme], pkeys: list[dict[str, ...]]
        ) -> list[ViewScheme]:
            if not data:
                return []

            await session.execute(
                sql_update(Model),
                params=[{**pkey, **obj.dict(exclude_unset=True)} for pkey, obj in zip(pkeys, data)],
            )
            await session.commit()

            return await self.batch_read(session, pkeys)

        async def delete(self, session: AsyncSession, **pkeys) -> None:
            q = delete(Model).where(pkey_clause(pkeys))
            await session.execute(q)
            await session.commit()

    return CRUD()
