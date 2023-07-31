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
    @staticmethod
    @abstractmethod
    async def create(session: AsyncSession, data: CreateType) -> ViewType:
        ...

    @staticmethod
    @abstractmethod
    async def create_if_not_exists(session: AsyncSession, data: CreateType) -> ViewType | None:
        ...

    @staticmethod
    @abstractmethod
    async def read(session: AsyncSession, **pkeys) -> ViewType | None:
        ...

    @staticmethod
    @abstractmethod
    async def batch_read(session: AsyncSession, pkeys: list[dict[str, ...]]) -> list[ViewType]:
        ...

    @staticmethod
    @abstractmethod
    async def read_all(session: AsyncSession) -> list[ViewType]:
        ...

    @staticmethod
    @abstractmethod
    async def read_by(session: AsyncSession, only_first: bool, **columns) -> list[ViewType] | ViewType | None:
        ...

    @staticmethod
    @abstractmethod
    async def update(session: AsyncSession, data: UpdateType, **pkeys) -> ViewType:
        ...

    @staticmethod
    @abstractmethod
    async def delete(session: AsyncSession, **pkeys) -> None:
        ...


# define generic type
ModelType = TypeVar("ModelType", bound=Base)


def CRUDFactory(
    Model: Type[ModelType],
    CreateScheme: Type[CreateType],
    ViewScheme: Type[ViewType],
    UpdateScheme: Type[UpdateType] = None,
    get_options: tuple[ExecutableOption, ...] = (),
) -> Type[AbstractCRUDRepository[CreateType, ViewType, UpdateType]]:
    from sqlalchemy import delete, insert, select, update
    from sqlalchemy.dialects.postgresql import insert as postgres_insert
    from sqlalchemy.inspection import inspect

    table = Model.__table__
    primary_keys = [column.name for column in inspect(table).primary_key]

    def pkey_clause(pkeys: dict[str, int]) -> ColumnElement["bool"]:
        return and_(*[getattr(Model, pk) == pkeys[pk] for pk in primary_keys])

    class CRUD(AbstractCRUDRepository[CreateScheme, ViewScheme, UpdateScheme], metaclass=ABCMeta):
        # ------------------ CREATE -------------- #
        @staticmethod
        async def create(session: AsyncSession, data: CreateScheme) -> ViewScheme:
            q = insert(Model).values(**data.dict()).returning(Model)
            if get_options:
                q = q.options(*get_options)
            obj = await session.scalar(q)
            await session.commit()
            return ViewScheme.from_orm(obj)

        @staticmethod
        async def create_if_not_exists(session: AsyncSession, data: CreateScheme) -> ViewScheme | None:
            q = postgres_insert(Model).values(**data.dict()).on_conflict_do_nothing().returning(Model)
            if get_options:
                q = q.options(*get_options)
            obj = await session.scalar(q)
            await session.commit()
            if obj:
                return ViewScheme.from_orm(obj)

        # ^^^^^^^^^^^^^^^^^^ CREATE ^^^^^^^^^^^^^^ #
        # ------------------ READ ---------------- #
        @staticmethod
        async def read(session: AsyncSession, **pkeys) -> ViewScheme:
            q = select(Model).where(pkey_clause(pkeys))
            if get_options:
                q = q.options(*get_options)
            obj = await session.scalar(q)
            if obj:
                return ViewScheme.from_orm(obj)

        @staticmethod
        async def batch_read(session: AsyncSession, pkeys: list[dict[str, ...]]) -> list[ViewScheme]:
            q = select(Model).where(or_(*[pkey_clause(pkey) for pkey in pkeys]))
            if get_options:
                q = q.options(*get_options)
            objs = await session.scalars(q)
            return [ViewScheme.from_orm(obj) for obj in objs]

        @staticmethod
        async def read_all(session: AsyncSession) -> list[ViewScheme]:
            q = select(Model)
            if get_options:
                q = q.options(*get_options)
            objs = await session.scalars(q)
            return [ViewScheme.from_orm(obj) for obj in objs]

        @staticmethod
        async def read_by(session: AsyncSession, only_first: bool, **columns) -> list[ViewScheme] | ViewScheme | None:
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
        @staticmethod
        async def update(session: AsyncSession, data: UpdateScheme, **pkeys) -> ViewScheme:
            q = update(Model).where(pkey_clause(pkeys)).values(**data.dict()).returning(Model)
            if get_options:
                q = q.options(*get_options)
            obj = await session.scalar(q)
            await session.commit()
            return ViewScheme.from_orm(obj)

        @staticmethod
        async def delete(session: AsyncSession, **pkeys) -> None:
            q = delete(Model).where(pkey_clause(pkeys))
            await session.execute(q)
            await session.commit()

    return CRUD
