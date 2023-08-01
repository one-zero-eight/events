import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import Settings, settings as config_settings
from src.repositories.event_groups import AbstractEventGroupRepository, SqlEventGroupRepository
from src.repositories.events import AbstractEventRepository, SqlEventRepository
from src.repositories.tags import AbstractTagRepository, SqlTagRepository
from src.repositories.users import AbstractUserRepository, SqlUserRepository
from src.storages.sql import AbstractSQLAlchemyStorage, SQLAlchemyStorage


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


# --- Storage Fixtures --- #
@pytest.fixture(scope="package")
def storage(settings: "Settings") -> "AbstractSQLAlchemyStorage":
    _storage = SQLAlchemyStorage.from_url(settings.DB_URL.get_secret_value())
    return _storage


@pytest_asyncio.fixture(scope="function", autouse=True)
async def setup_storage(storage: "AbstractSQLAlchemyStorage"):
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
def user_repository(storage) -> "AbstractUserRepository":
    return SqlUserRepository(storage)


@pytest.fixture(scope="package")
def event_group_repository(storage) -> "AbstractEventGroupRepository":
    return SqlEventGroupRepository(storage)


@pytest.fixture(scope="package")
def tag_repository(storage) -> "AbstractTagRepository":
    return SqlTagRepository(storage)


@pytest.fixture(scope="package")
def event_repository(storage) -> "AbstractEventRepository":
    return SqlEventRepository(storage)
