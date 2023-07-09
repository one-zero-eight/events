import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import Settings, settings as config_settings
from src.repositories.users import SqlUserRepository, AbstractUserRepository
from src.schemas.users import CreateUser, ViewUser
from src.storages.sql import SQLAlchemyStorage, AbstractSQLAlchemyStorage


@pytest.fixture(scope="package")
def settings() -> "Settings":
    return config_settings


@pytest.fixture(scope="package")
def storage(settings: "Settings") -> "AbstractSQLAlchemyStorage":
    _storage = SQLAlchemyStorage.from_url(settings.DB_URL.get_secret_value())
    return _storage


@pytest.fixture(scope="package")
def repository(storage) -> "AbstractUserRepository":
    return SqlUserRepository(storage)


@pytest_asyncio.fixture(scope="function", autouse=True)
async def setup_storage(storage: "AbstractSQLAlchemyStorage"):
    from sqlalchemy.sql import text

    # Clear all data from the database before each test
    async with storage.create_session() as session:
        session: AsyncSession
        q = text("DROP SCHEMA public CASCADE;")
        await session.execute(q)
        q = text("CREATE SCHEMA public;")
        await session.execute(q)

    # Create the necessary tables before each test
    await storage.create_all()
    yield
    # Close the database connection after each test
    await storage.close_connection()


@pytest.mark.asyncio
async def test_create_if_not_exists(repository):
    user_schema = CreateUser(email="test@innopolis.university", name="Test User")
    user = await repository.create_user_if_not_exists(user_schema)
    assert user is not None
    assert isinstance(user, ViewUser)
    assert user.id is not None
    assert user.email == user_schema.email
    assert user.name == user_schema.name
