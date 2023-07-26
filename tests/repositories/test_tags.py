import pytest
from faker import Faker

from src.schemas.tags import CreateTag, ViewTag, OwnershipEnum
from tests.repositories.test_users import _create_user
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.repositories.tags import AbstractTagRepository

fake = Faker()


def get_fake_tag() -> "CreateTag":
    return CreateTag(alias=fake.slug(), name=fake.name(), type=fake.slug(), satellite=fake.json(num_rows=1))


async def _create_tag(tag_repository: "AbstractTagRepository") -> "ViewTag":
    tag_schema = get_fake_tag()
    tag = await tag_repository.create_tag_if_not_exists(tag_schema)
    assert tag is not None
    assert isinstance(tag, ViewTag)
    assert tag.ownership_association == []
    assert tag.dict(exclude={"id", "ownership_association"}) == tag_schema.dict()
    return tag


async def _batch_create_tag(tag_repository: "AbstractTagRepository") -> list["ViewTag"]:
    tag_schemas = [get_fake_tag() for _ in range(10)]
    tags = await tag_repository.batch_create_tag_if_not_exists(tag_schemas)

    assert tags is not None
    assert isinstance(tags, list)
    assert len(tags) == len(tag_schemas)

    for tag, tag_schema in zip(tags, tag_schemas):
        assert tag is not None
        assert isinstance(tag, ViewTag)
        assert tag.dict(exclude={"id", "ownership_association"}) == tag_schema.dict()
    return tags


@pytest.mark.asyncio
async def test_get_tag_by_id(tag_repository):
    tag = await _create_tag(tag_repository)
    tag_by_id = await tag_repository.get_tag(tag.id)
    assert tag_by_id is not None
    assert isinstance(tag_by_id, ViewTag)
    assert tag_by_id.ownership_association == []
    assert tag.dict() == tag_by_id.dict()


@pytest.mark.asyncio
async def test_get_tags_by_ids(tag_repository):
    tags = await _batch_create_tag(tag_repository)
    tag_ids = [tag.id for tag in tags]
    tags_by_ids = await tag_repository.get_tags_by_ids(tag_ids)
    assert tags_by_ids is not None
    assert isinstance(tags_by_ids, list)
    assert len(tags_by_ids) == len(tags)
    for tag_by_id, tag in zip(tags_by_ids, tags):
        assert tag_by_id is not None
        assert isinstance(tag_by_id, ViewTag)
        assert tag_by_id.ownership_association == []
        assert tag_by_id.dict() == tag.dict()


@pytest.mark.asyncio
async def test_get_all_tags(tag_repository):
    tags = await _batch_create_tag(tag_repository)
    all_tags = await tag_repository.get_all_tags()
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
    tag_by_name = await tag_repository.get_tag_by_name(tag.name)
    assert tag_by_name is not None
    assert isinstance(tag_by_name, ViewTag)
    assert tag_by_name.ownership_association == []
    assert tag.dict() == tag_by_name.dict()


@pytest.mark.asyncio
async def test_create_tag_if_not_exists(tag_repository):
    await _create_tag(tag_repository)


@pytest.mark.asyncio
async def test_batch_create_tag_if_not_exists(tag_repository):
    await _batch_create_tag(tag_repository)


@pytest.mark.asyncio
async def test_setup_ownership(tag_repository, user_repository):
    user = await _create_user(user_repository)
    tag = await _create_tag(tag_repository)
    await tag_repository.setup_ownership(tag.id, user.id, OwnershipEnum.owner)
    tag_ownership = await tag_repository.get_tag(tag.id)
    assert tag_ownership is not None
    assert isinstance(tag_ownership, ViewTag)
    assert len(tag_ownership.ownership_association) == 1
    assert tag_ownership.ownership_association[0].user_id == user.id
    assert tag_ownership.ownership_association[0].tag_id == tag.id
    assert tag_ownership.ownership_association[0].ownership_enum == OwnershipEnum.owner
