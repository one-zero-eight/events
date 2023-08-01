import pytest
from faker import Faker

from src.schemas.tags import CreateTag, ViewTag, UpdateTag
from src.schemas import OwnershipEnum
from tests.repositories.test_users import _create_user
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.repositories.tags import AbstractTagRepository

fake = Faker()


def get_fake_tag() -> "CreateTag":
    return CreateTag(alias=fake.slug(), name=fake.name(), type=fake.slug(), satellite=fake.json(num_rows=1))


async def _create_tag(tag_repository: "AbstractTagRepository") -> "ViewTag":
    tag_schema = get_fake_tag()
    tag = await tag_repository.create_or_read(tag_schema)
    assert tag is not None
    assert isinstance(tag, ViewTag)
    assert tag.ownerships == []
    assert tag.dict(exclude={"id", "ownerships"}) == tag_schema.dict()
    return tag


async def _batch_create_tag(tag_repository: "AbstractTagRepository") -> list["ViewTag"]:
    tag_schemas = [get_fake_tag() for _ in range(10)]
    tags = await tag_repository.batch_create_or_read(tag_schemas)

    assert tags is not None
    assert isinstance(tags, list)
    assert len(tags) == len(tag_schemas)

    for tag, tag_schema in zip(tags, tag_schemas):
        assert tag is not None
        assert isinstance(tag, ViewTag)
        assert tag.dict(exclude={"id", "ownerships"}) == tag_schema.dict()
    return tags


@pytest.mark.asyncio
async def test_get_tag_by_id(tag_repository):
    tag = await _create_tag(tag_repository)
    tag_by_id = await tag_repository.read(tag.id)
    assert tag_by_id is not None
    assert isinstance(tag_by_id, ViewTag)
    assert tag_by_id.ownerships == []
    assert tag.dict() == tag_by_id.dict()


@pytest.mark.asyncio
async def test_get_tags_by_ids(tag_repository):
    tags = await _batch_create_tag(tag_repository)
    tag_ids = [tag.id for tag in tags]
    tags_by_ids = await tag_repository.batch_read(tag_ids)
    assert tags_by_ids is not None
    assert isinstance(tags_by_ids, list)
    assert len(tags_by_ids) == len(tags)
    for tag_by_id, tag in zip(tags_by_ids, tags):
        assert tag_by_id is not None
        assert isinstance(tag_by_id, ViewTag)
        assert tag_by_id.ownerships == []
        assert tag_by_id.dict() == tag.dict()


@pytest.mark.asyncio
async def test_get_all_tags(tag_repository):
    tags = await _batch_create_tag(tag_repository)
    all_tags = await tag_repository.read_all()
    assert all_tags is not None
    assert isinstance(all_tags, list)
    assert len(all_tags) == len(tags)
    for tag in all_tags:
        # find tag in tags
        assert tag.name in [tag.name for tag in tags]
        assert tag.id is not None


@pytest.mark.asyncio
async def test_get_tag_by_name(tag_repository):
    tag = await _create_tag(tag_repository)
    tag_by_name = await tag_repository.read_by_name(tag.name)
    assert tag_by_name is not None
    assert isinstance(tag_by_name, ViewTag)
    assert tag_by_name.ownerships == []
    assert tag.dict() == tag_by_name.dict()


@pytest.mark.asyncio
async def test_create_tag_if_not_exists(tag_repository):
    await _create_tag(tag_repository)


@pytest.mark.asyncio
async def test_create_existing_tag(tag_repository):
    tag_schema = get_fake_tag()
    tag = await tag_repository.create_or_read(tag_schema)
    existing = await tag_repository.create_or_read(tag_schema)
    assert tag.id == existing.id


@pytest.mark.asyncio
async def test_batch_create_tag_if_not_exists(tag_repository):
    await _batch_create_tag(tag_repository)


@pytest.mark.asyncio
async def test_setup_ownership(tag_repository, user_repository):
    user = await _create_user(user_repository)
    tag = await _create_tag(tag_repository)
    await tag_repository.setup_ownership(tag.id, user.id, OwnershipEnum.owner)
    updated_tag = await tag_repository.read(tag.id)
    assert updated_tag is not None
    assert isinstance(updated_tag, ViewTag)
    assert len(updated_tag.ownerships) == 1
    assert updated_tag.ownerships[0].user_id == user.id
    assert updated_tag.ownerships[0].object_id == tag.id
    assert updated_tag.ownerships[0].role_alias == OwnershipEnum.owner
    await tag_repository.setup_ownership(tag.id, user.id, OwnershipEnum.default)
    updated_tag = await tag_repository.read(tag.id)
    assert updated_tag is not None
    assert len(updated_tag.ownerships) == 0


@pytest.mark.asyncio
async def test_delete_tag(tag_repository):
    tag = await _create_tag(tag_repository)
    await tag_repository.delete(tag.id)
    tag_by_id = await tag_repository.read(tag.id)
    assert tag_by_id is None


@pytest.mark.asyncio
async def test_update_tag(tag_repository):
    tag_scheme = get_fake_tag()
    tag = await tag_repository.create_or_read(tag_scheme)
    assert tag is not None
    update_scheme = UpdateTag(name=fake.slug())
    updated_tag = await tag_repository.update(tag.id, update_scheme)
    assert updated_tag.id == tag.id
    assert updated_tag.name != tag.name
