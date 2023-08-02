import pytest
from faker import Faker

from src.schemas import OwnershipEnum
from src.schemas.tags import CreateTag, ViewTag, UpdateTag
from tests.repositories.test_users import _create_user

fake = Faker()


def get_fake_tag() -> "CreateTag":
    return CreateTag(
        alias=fake.slug(),
        name=fake.name(),
        type=fake.slug(),
        satellite={
            "meta": fake.slug(),
        },
    )


async def _create_tag(tag_repository) -> "ViewTag":
    tag_schema = get_fake_tag()
    tag = await tag_repository.create_or_read(tag_schema)
    assert tag is not None
    assert isinstance(tag, ViewTag)
    assert tag.ownerships == []
    assert tag.dict(exclude={"id", "ownerships"}) == tag_schema.dict()
    return tag


async def _batch_create_tag(tag_repository) -> list["ViewTag"]:
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


# ----------------- CRUD ----------------- #


@pytest.mark.asyncio
async def test_create_if_not_exists(tag_repository):
    await _create_tag(tag_repository)


@pytest.mark.asyncio
async def test_create_if_not_exists_HIT(tag_repository):
    tag_schema = get_fake_tag()
    tag = await tag_repository.create_or_read(tag_schema)
    hit = await tag_repository.create_or_read(tag_schema)
    assert tag.id == hit.id


@pytest.mark.asyncio
async def test_batch_create_tag_if_not_exists(tag_repository):
    await _batch_create_tag(tag_repository)


@pytest.mark.asyncio
async def test_read(tag_repository):
    tag = await _create_tag(tag_repository)
    hit = await tag_repository.read(tag.id)
    assert hit.id == tag.id


@pytest.mark.asyncio
async def test_batch_read(tag_repository):
    tags = await _batch_create_tag(tag_repository)
    tag_ids = [tag.id for tag in tags]
    tags_by_ids = await tag_repository.batch_read(tag_ids)
    assert isinstance(tags_by_ids, list)
    assert len(tags_by_ids) == len(tags)
    for tag_by_id, tag in zip(tags_by_ids, tags):
        assert tag_by_id.id == tag.id


@pytest.mark.asyncio
async def test_read_all(tag_repository):
    tags = await _batch_create_tag(tag_repository)
    all_tags = await tag_repository.read_all()
    assert isinstance(all_tags, list)
    assert len(all_tags) == len(tags)
    for tag in all_tags:
        assert tag.id in {tag.id for tag in tags}


@pytest.mark.asyncio
async def test_read_by_name(tag_repository):
    tag = await _create_tag(tag_repository)
    tag_by_name = await tag_repository.read_by_name(tag.name)
    assert tag_by_name.id == tag.id


@pytest.mark.asyncio
async def test_update(tag_repository):
    tag_scheme = get_fake_tag()
    tag = await tag_repository.create_or_read(tag_scheme)
    assert tag is not None
    update_scheme = UpdateTag(name=fake.slug(), satellite={"metadata": "updated metadata"})
    updated_tag = await tag_repository.update(tag.id, update_scheme)
    assert updated_tag.id == tag.id
    assert updated_tag.name != tag.name


@pytest.mark.asyncio
async def test_delete(tag_repository):
    tag = await _create_tag(tag_repository)
    await tag_repository.delete(tag.id)
    tag_by_id = await tag_repository.read(tag.id)
    assert tag_by_id is None


# ^^^^^^^^^^^^^^^^^^ CRUD ^^^^^^^^^^^^^^^^^^ #
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
    await tag_repository.setup_ownership(tag.id, user.id, OwnershipEnum.delete)
    updated_tag = await tag_repository.read(tag.id)
    assert updated_tag is not None
    assert len(updated_tag.ownerships) == 0
