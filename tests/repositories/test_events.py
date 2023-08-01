from typing import TYPE_CHECKING

import pytest
from faker import Faker

from src.schemas import AddEventPatch
from src.schemas.events import CreateEvent, ViewEvent, UpdateEvent, ViewEventPatch

if TYPE_CHECKING:
    from src.repositories.events import AbstractEventRepository

fake = Faker()


def get_fake_event() -> "CreateEvent":
    return CreateEvent(name=fake.name(), description=fake.slug())


def get_fake_event_patch() -> "AddEventPatch":
    return AddEventPatch(
        summary=fake.slug(),
        description=fake.slug(),
        dtstart=fake.date_time(),
        dtend=fake.date_time(),
        rrule={
            "freq": "DAILY",
            "until": fake.date_time(),
            "interval": 1,
        },
    )


async def _create_event(event_repository: "AbstractEventRepository") -> "ViewEvent":
    event_schema = get_fake_event()
    event = await event_repository.create(event_schema)
    assert event is not None
    assert isinstance(event, ViewEvent)
    assert event.id is not None
    assert event.name == event_schema.name
    return event


@pytest.mark.asyncio
async def test_create(event_repository):
    await _create_event(event_repository)


@pytest.mark.asyncio
async def test_add_patch(event_repository):
    event = await _create_event(event_repository)
    event_patch = get_fake_event_patch()
    event_patch = await event_repository.add_patch(event.id, event_patch)
    assert event_patch is not None
    assert isinstance(event_patch, ViewEventPatch)
    assert event_patch.id is not None
    assert event_patch.summary == event_patch.summary
    assert event_patch.parent_id == event.id


@pytest.mark.asyncio
async def test_create_with_patches(event_repository):
    event = get_fake_event()
    event.patches = [
        AddEventPatch(**fake_event_patch.dict()) for fake_event_patch in [get_fake_event_patch() for _ in range(10)]
    ]

    db_event = await event_repository.create(event)
    assert db_event is not None
    assert isinstance(db_event, ViewEvent)
    assert db_event.id is not None
    assert db_event.name == event.name
    assert len(db_event.patches) == len(event.patches)


@pytest.mark.asyncio
async def test_read(event_repository):
    event = await _create_event(event_repository)
    event = await event_repository.read(event.id)
    assert event is not None
    assert isinstance(event, ViewEvent)
    assert event.id is not None
    assert event.name == event.name
    assert len(event.patches) == 0


@pytest.mark.asyncio
async def test_read_with_patches(event_repository):
    event = get_fake_event()
    event.patches = [
        AddEventPatch(**fake_event_patch.dict()) for fake_event_patch in [get_fake_event_patch() for _ in range(10)]
    ]

    db_event = await event_repository.create(event)
    assert db_event is not None
    assert isinstance(db_event, ViewEvent)
    assert db_event.id is not None
    assert db_event.name == event.name
    assert len(db_event.patches) == len(event.patches)

    db_event = await event_repository.read(db_event.id)
    assert db_event is not None
    assert isinstance(db_event, ViewEvent)
    assert db_event.id is not None
    assert db_event.name == event.name
    assert len(db_event.patches) == len(event.patches)

    patches = await event_repository.read_patches(db_event.id)
    assert patches is not None
    assert isinstance(patches, list)
    assert len(patches) == len(event.patches)
    for patch in patches:
        assert isinstance(patch, ViewEventPatch)
        assert patch.id is not None
        assert patch.parent_id == db_event.id


@pytest.mark.asyncio
async def test_update(event_repository):
    event = await _create_event(event_repository)
    event_schema = get_fake_event()
    event = await event_repository.update(
        event.id, UpdateEvent(name=event_schema.name, description=event_schema.description)
    )
    assert event is not None
    assert isinstance(event, ViewEvent)
    assert event.id is not None
    assert event.name == event_schema.name


@pytest.mark.asyncio
async def test_delete(event_repository):
    event = await _create_event(event_repository)
    await event_repository.delete(event.id)
    event = await event_repository.read(event.id)
    assert event is None
