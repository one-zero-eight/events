import pytest
from faker import Faker

from src.schemas.event_groups import CreateEventGroup, ViewEventGroup

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.repositories.event_groups import AbstractEventGroupRepository

fake = Faker()


def get_fake_event_group() -> "CreateEventGroup":
    fake_json = fake.json()
    fake_path = fake.slug()
    fake_type = fake.slug()
    return CreateEventGroup(name=fake.name(), type=fake_type, path=fake_path, satellite=fake_json)


async def _create_event_group(event_group_repository: "AbstractEventGroupRepository") -> "ViewEventGroup":
    event_group_schema = get_fake_event_group()
    event_group = await event_group_repository.create_group_if_not_exists(event_group_schema)
    assert event_group is not None
    assert isinstance(event_group, ViewEventGroup)
    assert event_group.id is not None
    assert event_group.name == event_group_schema.name
    assert event_group.path == event_group_schema.path
    return event_group


async def _batch_create_event_group(event_group_repository: "AbstractEventGroupRepository") -> list["ViewEventGroup"]:
    event_group_schemas = [get_fake_event_group() for _ in range(10)]
    event_groups = await event_group_repository.batch_create_group_if_not_exists(event_group_schemas)

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

    return event_groups


@pytest.mark.asyncio
async def test_create_if_not_exists(event_group_repository):
    event_group_schema = get_fake_event_group()
    event_group = await event_group_repository.create_group_if_not_exists(event_group_schema)
    assert event_group is not None
    assert isinstance(event_group, ViewEventGroup)
    assert event_group.id is not None
    assert event_group.name == event_group_schema.name


@pytest.mark.asyncio
async def test_batch_create_if_not_exists(event_group_repository):
    await _batch_create_event_group(event_group_repository)


@pytest.mark.asyncio
async def test_get_by_id(event_group_repository):
    event_group = await _create_event_group(event_group_repository)
    gotten_event_group = await event_group_repository.get_group(event_group.id)
    assert gotten_event_group is not None
    assert isinstance(gotten_event_group, ViewEventGroup)
    assert gotten_event_group.id is not None
    assert gotten_event_group.name == event_group.name


@pytest.mark.asyncio
async def test_get_by_path(event_group_repository):
    event_group = await _create_event_group(event_group_repository)
    gotten_event_group = await event_group_repository.get_group_by_path(event_group.path)
    assert gotten_event_group is not None
    assert isinstance(gotten_event_group, ViewEventGroup)
    assert gotten_event_group.id is not None
    assert gotten_event_group.name == event_group.name


@pytest.mark.asyncio
async def test_get_all(event_group_repository):
    event_groups = await _batch_create_event_group(event_group_repository)
    gotten_event_groups = await event_group_repository.get_all_groups()
    assert gotten_event_groups is not None
    assert isinstance(gotten_event_groups, list)
    assert len(gotten_event_groups) == len(event_groups)
