import pytest
from faker import Faker

from src.schemas import AddEventPatch
from src.schemas.events import CreateEvent, ViewEvent, UpdateEvent, ViewEventPatch, UpdateEventPatch

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


async def _create_event(event_repository) -> "ViewEvent":
    scheme = get_fake_event()
    event = await event_repository.create(scheme)
    assert event is not None
    assert isinstance(event, ViewEvent)
    assert event.id is not None
    assert event.name == scheme.name
    return event


# ------------------- CRUD ------------------- #


@pytest.mark.asyncio
async def test_create(event_repository):
    await _create_event(event_repository)


@pytest.mark.asyncio
async def test_create_with_patches(event_repository):
    scheme = get_fake_event()
    scheme.patches = [
        AddEventPatch(**fake_event_patch.dict()) for fake_event_patch in [get_fake_event_patch() for _ in range(10)]
    ]
    event = await event_repository.create(scheme)
    assert isinstance(event, ViewEvent)
    assert event.id is not None
    assert event.name == scheme.name
    assert len(event.patches) == len(scheme.patches)


@pytest.mark.asyncio
async def test_read(event_repository):
    event = await _create_event(event_repository)
    hit = await event_repository.read(event.id)
    assert isinstance(hit, ViewEvent)
    assert hit.id == event.id


@pytest.mark.asyncio
async def test_update(event_repository):
    event = await _create_event(event_repository)
    updated = await event_repository.update(event.id, UpdateEvent(name=fake.slug(), description=fake.text()))
    assert isinstance(updated, ViewEvent)
    assert updated.id == event.id
    assert updated.name != event.name
    assert updated.description != event.description


@pytest.mark.asyncio
async def test_delete(event_repository):
    event = await _create_event(event_repository)
    await event_repository.delete(event.id)
    event = await event_repository.read(event.id)
    assert event is None


# ^^^^^^^^^^^^^^^^^^^ CRUD ^^^^^^^^^^^^^^^^^^^ #
# ------------------- PATCHES ------------------- #


@pytest.mark.asyncio
async def test_add_patch(event_repository):
    event = await _create_event(event_repository)
    event_patch_scheme = get_fake_event_patch()
    event_patch = await event_repository.add_patch(event.id, event_patch_scheme)
    assert event_patch is not None
    assert isinstance(event_patch, ViewEventPatch)
    assert event_patch.id is not None
    assert event_patch.summary == event_patch_scheme.summary
    assert event_patch.parent_id == event.id


@pytest.mark.asyncio
async def test_read_patches(event_repository):
    scheme = get_fake_event()
    scheme.patches = [
        AddEventPatch(**fake_event_patch.dict()) for fake_event_patch in [get_fake_event_patch() for _ in range(10)]
    ]

    event = await event_repository.create(scheme)
    patches = await event_repository.read_patches(event.id)
    assert isinstance(patches, list)
    assert len(patches) == len(scheme.patches)
    for patch in patches:
        assert isinstance(patch, ViewEventPatch)
        assert patch.id is not None
        assert patch.parent_id == event.id


@pytest.mark.asyncio
async def test_update_patch(event_repository):
    event = await _create_event(event_repository)
    event_patch = get_fake_event_patch()
    event_patch = await event_repository.add_patch(event.id, event_patch)
    updated_event_patch = await event_repository.update_patch(event_patch.id, UpdateEventPatch(summary=fake.slug()))
    assert isinstance(updated_event_patch, ViewEventPatch)
    assert updated_event_patch.id == event_patch.id
    assert updated_event_patch.summary != event_patch.summary


# ^^^^^^^^^^^^^^^^^^^ PATCHES ^^^^^^^^^^^^^^^^^^^ #
