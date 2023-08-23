import pytest
from faker import Faker
from sqlalchemy.exc import IntegrityError

from src.repositories.event_groups import AbstractEventGroupRepository
from src.schemas.event_groups import CreateEventGroup, ViewEventGroup, UpdateEventGroup

fake = Faker()


def get_fake_event_group() -> "CreateEventGroup":
    fake_path = fake.slug()
    return CreateEventGroup(alias=fake.slug(), name=fake.name(), path=fake_path, description=fake.slug())


async def _create_event_group(event_group_repository: AbstractEventGroupRepository) -> "ViewEventGroup":
    event_group_schema = get_fake_event_group()
    event_group = await event_group_repository.create(event_group_schema)
    assert event_group is not None
    assert isinstance(event_group, ViewEventGroup)
    assert event_group.id is not None
    assert event_group.name == event_group_schema.name
    assert event_group.path == event_group_schema.path
    return event_group


async def _batch_create_event_group(event_group_repository: AbstractEventGroupRepository) -> list["ViewEventGroup"]:
    event_group_schemas = [get_fake_event_group() for _ in range(10)]
    event_groups = await event_group_repository.batch_create(event_group_schemas)

    assert event_groups is not None
    assert isinstance(event_groups, list)
    assert len(event_groups) == len(event_group_schemas)

    for event_group, event_group_schema in zip(event_groups, event_group_schemas):
        assert event_group is not None
        assert isinstance(event_group, ViewEventGroup)
        assert event_group.id is not None
        assert event_group.name == event_group_schema.name
        assert event_group.path == event_group_schema.path

    return event_groups


# ----------------- CRUD ----------------- #
@pytest.mark.asyncio
async def test_create_if_not_exists(event_group_repository):
    await _create_event_group(event_group_repository)


@pytest.mark.asyncio
async def test_create_if_not_exists_HIT(event_group_repository):
    event_group_schema = get_fake_event_group()
    event_group = await event_group_repository.create(event_group_schema)
    assert isinstance(event_group, ViewEventGroup)

    with pytest.raises(IntegrityError):
        await event_group_repository.create(event_group_schema)


@pytest.mark.asyncio
async def test_batch_create_if_not_exists(event_group_repository):
    await _batch_create_event_group(event_group_repository)


@pytest.mark.asyncio
async def test_read(event_group_repository):
    event_group = await _create_event_group(event_group_repository)
    hit = await event_group_repository.read(event_group.id)
    assert hit.id == event_group.id


@pytest.mark.asyncio
async def test_read_by_path(event_group_repository):
    event_group = await _create_event_group(event_group_repository)
    hit = await event_group_repository.read_by_path(event_group.path)
    assert hit.id == event_group.id


@pytest.mark.asyncio
async def test_read_all(event_group_repository):
    event_groups = await _batch_create_event_group(event_group_repository)
    gotten_event_groups = await event_group_repository.read_all()
    assert isinstance(gotten_event_groups, list)
    assert len(gotten_event_groups) == len(event_groups)


@pytest.mark.asyncio
async def test_update(event_group_repository):
    event_group = await _create_event_group(event_group_repository)
    update_scheme = UpdateEventGroup(path="updated-path", name="updated-name")
    updated_event_group = await event_group_repository.update(event_group.id, update_scheme)
    assert updated_event_group.id == event_group.id
    assert updated_event_group.path == "updated-path"
    assert updated_event_group.name == "updated-name"


# ^^^^^^^^^^^^^^^^^^^^ CRUD ^^^^^^^^^^^^^^^^^^^^ #
@pytest.mark.asyncio
async def test_path_duplicate(event_group_repository):
    event_group = await _create_event_group(event_group_repository)
    assert isinstance(event_group, ViewEventGroup)
    new_scheme = CreateEventGroup(alias=fake.slug(), name=fake.name(), path=event_group.path)
    with pytest.raises(IntegrityError):
        await event_group_repository.create(new_scheme)


@pytest.mark.asyncio
async def test_null_path(event_group_repository):
    scheme = CreateEventGroup(alias=fake.slug(), name=fake.name())
    new_scheme = CreateEventGroup(alias=fake.slug(), name=fake.name())
    event_group = await event_group_repository.create(scheme)
    new_event_group = await event_group_repository.create(new_scheme)
    assert event_group.id != new_event_group.id


@pytest.mark.asyncio
async def test_batch_read_with_ordering(event_group_repository):
    event_group1 = await _create_event_group(event_group_repository)
    event_group2 = await _create_event_group(event_group_repository)
    event_group3 = await _create_event_group(event_group_repository)
    event_groups = await event_group_repository.batch_read([event_group3.id, event_group2.id, event_group1.id])
    assert event_groups[0].id == event_group3.id
    assert event_groups[1].id == event_group2.id
    assert event_groups[2].id == event_group1.id
