import httpx
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import Settings, settings as config_settings
from src.api.main import app
from src.repositories.event_groups import SqlEventGroupRepository
from src.repositories.events import SqlEventRepository
from src.repositories.tags import SqlTagRepository
from src.repositories.users import SqlUserRepository

# from src.repositories.workshops import AbstractWorkshopRepository, SqlWorkshopRepository
from src.storages.sql import SQLAlchemyStorage


# --- Monkey Patching --- #
@pytest.fixture(scope="session")
def monkeysession():
    from _pytest.monkeypatch import MonkeyPatch

    mpatch = MonkeyPatch()
    yield mpatch
    mpatch.undo()


# --- Settings Fixtures --- #
@pytest.fixture(scope="package")
def settings() -> "Settings":
    return config_settings


@pytest_asyncio.fixture()
async def client():
    async with httpx.AsyncClient(app=app, base_url="http://127.0.0.1:8000/") as client:
        yield client


# --- Storage Fixtures --- #
@pytest.fixture(scope="package")
def storage(settings: "Settings") -> "SQLAlchemyStorage":
    _storage = SQLAlchemyStorage.from_url(settings.db_url.get_secret_value())
    return _storage


@pytest_asyncio.fixture(scope="function", autouse=True)
async def setup_storage(storage: "SQLAlchemyStorage"):
    # Create the necessary tables before each test
    async with storage.create_session() as session:
        await _init_models(session)
        await session.commit()
    yield

    # Close the database connection after each test
    async with storage.create_session() as session:
        await _restore_session(session)
        await session.commit()
    await storage.close_connection()


async def _init_models(session: AsyncSession):
    from src.storages.sql.models.base import Base

    async with session.bind.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


async def _restore_session(session: AsyncSession):
    from src.storages.sql.models.base import Base

    async with session.begin():
        for table in reversed(Base.metadata.sorted_tables):
            await session.execute(table.delete())


# --- Repository Fixtures --- #


@pytest.fixture(scope="package")
def user_repository(storage) -> "SqlUserRepository":
    return SqlUserRepository(storage)


@pytest.fixture(scope="package")
def event_group_repository(storage) -> "SqlEventGroupRepository":
    return SqlEventGroupRepository(storage)


@pytest.fixture(scope="package")
def tag_repository(storage) -> "SqlTagRepository":
    return SqlTagRepository(storage)


@pytest.fixture(scope="package")
def event_repository(storage) -> "SqlEventRepository":
    return SqlEventRepository(storage)


# @pytest.fixture(scope="package")
# def workshop_repository(storage) -> "AbstractWorkshopRepository":
#     return SqlWorkshopRepository(storage)
