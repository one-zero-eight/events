import pytest
import pytest_asyncio
from faker import Faker
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import Settings, settings as config_settings
from src.repositories.users import SqlUserRepository, AbstractUserRepository
from src.schemas.users import CreateUser, ViewUser
from src.storages.sql import SQLAlchemyStorage, AbstractSQLAlchemyStorage

fake = Faker()


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
    user_schema = CreateUser(email=fake.email(), name=fake.name())
    user = await repository.create_user_if_not_exists(user_schema)
    assert user is not None
    assert isinstance(user, ViewUser)
    assert user.id is not None
    assert user.email == user_schema.email
    assert user.name == user_schema.name


@pytest.mark.asyncio
async def test_upsert_user(repository):
    # Create a new user
    user_schema = CreateUser(email=fake.email(), name=fake.name())
    user = await repository.upsert_user(user_schema)
    assert user is not None
    assert isinstance(user, ViewUser)
    assert user.id is not None
    assert user.email == user_schema.email
    assert user.name == user_schema.name

    # Update an existing user
    updated_user_schema = CreateUser(email=user_schema.email, name=fake.name())
    updated_user = await repository.upsert_user(updated_user_schema)
    assert updated_user is not None
    assert isinstance(updated_user, ViewUser)
    assert updated_user.id == user.id
    assert updated_user.email == updated_user_schema.email
    assert updated_user.name == updated_user_schema.name


@pytest.mark.asyncio
async def test_batch_create_user_if_not_exists(repository):
    # Create a batch of new users
    user_schemas = [
        CreateUser(email=fake.email(), name=fake.name()),
        CreateUser(email=fake.email(), name=fake.name()),
        CreateUser(email=fake.email(), name=fake.name()),
    ]
    users = await repository.batch_create_user_if_not_exists(user_schemas)
    assert len(users) == len(user_schemas)
    for user, user_schema in zip(users, user_schemas):
        assert user is not None
        assert isinstance(user, ViewUser)
        assert user.id is not None
        assert user.email == user_schema.email
        assert user.name == user_schema.name


@pytest.mark.asyncio
async def test_get_user_id_by_email(repository):
    # Create a new user
    user_schema = CreateUser(email=fake.email(), name=fake.name())
    await repository.create_user_if_not_exists(user_schema)

    # Retrieve the user ID by email
    user_id = await repository.get_user_id_by_email(user_schema.email)
    assert user_id is not None
    assert isinstance(user_id, int)


@pytest.mark.asyncio
async def test_get_user(repository):
    # Create a new user
    user_schema = CreateUser(email=fake.email(), name=fake.name())
    created_user = await repository.create_user_if_not_exists(user_schema)

    # Retrieve the user by ID
    retrieved_user = await repository.get_user(created_user.id)
    assert retrieved_user is not None
    assert isinstance(retrieved_user, ViewUser)
    assert retrieved_user.id == created_user.id
    assert retrieved_user.email == created_user.email
    assert retrieved_user.name == created_user.name


@pytest.mark.asyncio
async def test_batch_get_user(repository):
    # Create a batch of new users
    user_schemas = [
        CreateUser(email=fake.email(), name=fake.name()),
        CreateUser(email=fake.email(), name=fake.name()),
        CreateUser(email=fake.email(), name=fake.name()),
    ]
    created_users = await repository.batch_create_user_if_not_exists(user_schemas)

    # Retrieve the users by their IDs
    user_ids = [user.id for user in created_users]
    retrieved_users = await repository.batch_get_user(user_ids)
    assert len(retrieved_users) == len(created_users)
    for retrieved_user, created_user in zip(retrieved_users, created_users):
        assert retrieved_user is not None
        assert isinstance(retrieved_user, ViewUser)
        assert retrieved_user.id == created_user.id
        assert retrieved_user.email == created_user.email
        assert retrieved_user.name == created_user.name
