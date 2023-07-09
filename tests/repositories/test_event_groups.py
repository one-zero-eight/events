import pytest
import pytest_asyncio
from faker import Faker
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import Settings, settings as config_settings
from src.repositories.event_groups import SqlEventGroupRepository, AbstractEventGroupRepository
from src.schemas.event_groups import CreateEventGroup, ViewEventGroup
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
def repository(storage) -> "AbstractEventGroupRepository":
    return SqlEventGroupRepository(storage)


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


def get_fake_event_group() -> "CreateEventGroup":
    fake_json = fake.json()
    fake_path = fake.slug()
    fake_type = fake.slug()
    return CreateEventGroup(name=fake.name(), type=fake_type, path=fake_path, satellite=fake_json)


@pytest.mark.asyncio
async def test_create_if_not_exists(repository: "AbstractEventGroupRepository"):
    event_group_schema = get_fake_event_group()
    event_group = await repository.create_group_if_not_exists(event_group_schema)
    assert event_group is not None
    assert isinstance(event_group, ViewEventGroup)
    assert event_group.id is not None
    assert event_group.name == event_group_schema.name


@pytest.mark.asyncio
async def test_batch_create_if_not_exists(repository: "AbstractEventGroupRepository"):
    event_group_schemas = [get_fake_event_group() for _ in range(10)]
    event_groups = await repository.batch_create_group_if_not_exists(event_group_schemas)
    assert event_groups is not None
    assert isinstance(event_groups, list)
    assert len(event_groups) == len(event_group_schemas)

    for event_group, event_group_schema in zip(event_groups, event_group_schemas):
        assert event_group is not None
        assert isinstance(event_group, ViewEventGroup)
        assert event_group.id is not None
        assert event_group.name == event_group_schema.name
        assert event_group.path == event_group_schema.path
        assert event_group.type == event_group_schema.type


@pytest.mark.asyncio
async def test_get_by_id(repository: "AbstractEventGroupRepository"):
    event_group_schema = get_fake_event_group()
    event_group = await repository.create_group_if_not_exists(event_group_schema)
    assert event_group is not None
    assert isinstance(event_group, ViewEventGroup)
    assert event_group.id is not None
    assert event_group.name == event_group_schema.name
    event_group = await repository.get_group(event_group.id)
    assert event_group is not None
    assert isinstance(event_group, ViewEventGroup)
    assert event_group.id is not None
    assert event_group.name == event_group_schema.name


@pytest.mark.asyncio
async def test_get_by_path(repository: "AbstractEventGroupRepository"):
    event_group_schema = get_fake_event_group()
    event_group = await repository.create_group_if_not_exists(event_group_schema)
    assert event_group is not None
    assert isinstance(event_group, ViewEventGroup)
    assert event_group.id is not None
    assert event_group.name == event_group_schema.name
    event_group = await repository.get_group_by_path(event_group.path)
    assert event_group is not None
    assert isinstance(event_group, ViewEventGroup)
    assert event_group.id is not None
    assert event_group.name == event_group_schema.name


@pytest.mark.asyncio
async def test_get_all(repository: "AbstractEventGroupRepository"):
    event_group_schemas = [get_fake_event_group() for _ in range(10)]
    event_groups = await repository.batch_create_group_if_not_exists(event_group_schemas)
    assert event_groups is not None
    assert isinstance(event_groups, list)
    assert len(event_groups) == len(event_group_schemas)

    event_groups = await repository.get_all_groups()
    assert event_groups is not None
    assert isinstance(event_groups, list)
    assert len(event_groups) >= len(event_group_schemas)
