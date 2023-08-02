import pytest

from src.schemas import OwnershipEnum
from tests.repositories.test_event_groups import _create_event_group
from tests.repositories.test_tags import _create_tag
from tests.repositories.test_users import _create_user


async def _test_setup_ownership(
    user,
    target,
    target_repository,
):
    await target_repository.setup_ownership(target.id, user.id, OwnershipEnum.owner)
    updated_target = await target_repository.read(target.id)
    assert updated_target is not None
    count_of_ownerships = len(updated_target.ownerships)
    ownership = updated_target.ownerships[-1]
    assert ownership.user_id == user.id
    assert ownership.object_id == target.id
    assert ownership.role_alias == OwnershipEnum.owner
    await target_repository.setup_ownership(target.id, user.id, OwnershipEnum.delete)
    updated_target = await target_repository.read(target.id)
    assert updated_target is not None
    assert len(updated_target.ownerships) == count_of_ownerships - 1


@pytest.mark.asyncio
async def test_tag_setup_ownership(tag_repository, user_repository):
    user = await _create_user(user_repository)
    target = await _create_tag(tag_repository)
    await _test_setup_ownership(user, target, tag_repository)


@pytest.mark.asyncio
async def test_event_group_setup_ownership(event_group_repository, user_repository):
    user = await _create_user(user_repository)
    target = await _create_event_group(event_group_repository)
    await _test_setup_ownership(user, target, event_group_repository)
