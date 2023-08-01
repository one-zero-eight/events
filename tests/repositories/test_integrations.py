import random
from typing import TYPE_CHECKING

import pytest
from faker import Faker

from src.schemas import ViewTag
from src.schemas.event_groups import UserXFavoriteGroupView, ViewEventGroup
from src.schemas.users import ViewUser
from tests.repositories.test_event_groups import _create_event_group, _batch_create_event_group
from tests.repositories.test_users import _create_user, _batch_create_user_if_not_exists
from tests.repositories.test_tags import _create_tag, _batch_create_tag

if TYPE_CHECKING:
    from src.repositories.users import AbstractUserRepository
    from src.repositories.event_groups import AbstractEventGroupRepository
fake = Faker()


#   INTEGRATION BETWEEN USERS AND EVENT_GROUPS
@pytest.mark.asyncio
async def test_setup_groups(
    event_group_repository: "AbstractEventGroupRepository", user_repository: "AbstractUserRepository"
):
    user = await _create_user(user_repository)
    event_group = await _create_event_group(event_group_repository)
    await event_group_repository.setup_groups(user.id, [event_group.id])

    updated_user = await user_repository.read(user.id)
    assert len(updated_user.favorites_association) == 1
    user_x_group = updated_user.favorites_association[0]
    assert isinstance(user_x_group, UserXFavoriteGroupView)
    assert user_x_group.predefined is True
    assert user_x_group.user_id == user.id
    assert user_x_group.event_group.id == event_group.id


@pytest.mark.asyncio
async def test_batch_setup_groups(
    event_group_repository: "AbstractEventGroupRepository", user_repository: "AbstractUserRepository"
):
    users = await _batch_create_user_if_not_exists(user_repository)
    event_groups = await _batch_create_event_group(event_group_repository)
    # random mapping
    mapping = {
        user.id: random.sample([event_group.id for event_group in event_groups], random.randint(1, 5)) for user in users
    }
    await event_group_repository.batch_setup_groups(mapping)

    updated_users = await user_repository.batch_read([user.id for user in users])
    assert updated_users is not None
    assert isinstance(updated_users, list)
    assert len(updated_users) == 10
    for updated_user in updated_users:
        assert updated_user is not None
        assert isinstance(updated_user, ViewUser)
        assert updated_user.id in [user.id for user in users]
        assert updated_user.email in [user.email for user in users]
        assert updated_user.name in [user.name for user in users]
        assert updated_user.favorites_association is not None
        assert len(updated_user.favorites_association) in [1, 2, 3, 4, 5]
        for user_x_group in updated_user.favorites_association:
            assert isinstance(user_x_group, UserXFavoriteGroupView)
            assert user_x_group.predefined is True
            assert user_x_group.user_id == updated_user.id
            assert user_x_group.event_group.id in mapping[updated_user.id]


@pytest.mark.asyncio
async def test_set_hidden(
    event_group_repository: "AbstractEventGroupRepository", user_repository: "AbstractUserRepository"
):
    user = await _create_user(user_repository)
    event_group = await _create_event_group(event_group_repository)

    await event_group_repository.setup_groups(user.id, [event_group.id])

    updated_user = await user_repository.read(user.id)
    assert updated_user.favorites_association is not None
    assert len(updated_user.favorites_association) == 1
    user_x_group = updated_user.favorites_association[0]
    assert isinstance(user_x_group, UserXFavoriteGroupView)
    assert user_x_group.user_id == user.id
    assert user_x_group.event_group.id == event_group.id
    assert user_x_group.hidden is False

    await user_repository.set_hidden(user.id, event_group.id, True)

    updated_user = await user_repository.read(user.id)
    assert updated_user.favorites_association is not None
    assert len(updated_user.favorites_association) == 1
    user_x_group = updated_user.favorites_association[0]
    assert isinstance(user_x_group, UserXFavoriteGroupView)
    assert user_x_group.user_id == user.id
    assert user_x_group.event_group.id == event_group.id
    assert user_x_group.hidden is True


@pytest.mark.asyncio
async def test_add_favorite(
    event_group_repository: "AbstractEventGroupRepository", user_repository: "AbstractUserRepository"
):
    user = await _create_user(user_repository)
    event_group = await _create_event_group(event_group_repository)

    updated_user = await user_repository.add_favorite(user.id, event_group.id)
    assert updated_user is not None
    assert isinstance(updated_user, ViewUser)
    assert updated_user.id == user.id
    assert updated_user.email == user.email
    assert updated_user.name == user.name
    assert updated_user.favorites_association is not None
    assert len(updated_user.favorites_association) == 1
    user_x_group = updated_user.favorites_association[0]
    assert isinstance(user_x_group, UserXFavoriteGroupView)
    assert user_x_group.user_id == user.id
    assert user_x_group.event_group.id == event_group.id
    assert user_x_group.predefined is False


@pytest.mark.asyncio
async def test_add_favorite_with_wrong_group(
    event_group_repository: "AbstractEventGroupRepository", user_repository: "AbstractUserRepository"
):
    from src.exceptions import DBEventGroupDoesNotExistInDb

    user = await _create_user(user_repository)
    NOT_EXISTING_GROUP_ID = 1
    with pytest.raises(DBEventGroupDoesNotExistInDb):
        await user_repository.add_favorite(user.id, NOT_EXISTING_GROUP_ID)


@pytest.mark.asyncio
async def test_remove_favorite(
    event_group_repository: "AbstractEventGroupRepository", user_repository: "AbstractUserRepository"
):
    user = await _create_user(user_repository)
    event_group = await _create_event_group(event_group_repository)

    await user_repository.add_favorite(user.id, event_group.id)

    updated_user = await user_repository.remove_favorite(user.id, event_group.id)
    assert updated_user is not None
    assert isinstance(updated_user, ViewUser)
    assert updated_user.id == user.id
    assert updated_user.email == user.email
    assert updated_user.name == user.name
    assert updated_user.favorites_association is not None
    assert len(updated_user.favorites_association) == 0


@pytest.mark.asyncio
async def test_add_tags_to_event_group(event_group_repository, tag_repository):
    event_group = await _create_event_group(event_group_repository)
    tags = await _batch_create_tag(tag_repository)
    await tag_repository.add_tags_to_event_group(event_group.id, [tag.id for tag in tags])

    updated_event_group = await event_group_repository.read(event_group.id)
    assert updated_event_group is not None
    assert isinstance(updated_event_group, ViewEventGroup)
    assert updated_event_group.id == event_group.id
    assert updated_event_group.name == event_group.name
    assert updated_event_group.description == event_group.description
    assert updated_event_group.tags is not None
    assert len(updated_event_group.tags) == len(tags)
    for tag in updated_event_group.tags:
        assert isinstance(tag, ViewTag)
        assert tag.id in {tag.id for tag in tags}
        assert tag.name in {tag.name for tag in tags}


@pytest.mark.asyncio
async def test_batch_add_tags_to_event_group(event_group_repository, tag_repository):
    event_groups = await _batch_create_event_group(event_group_repository)
    tags = await _batch_create_tag(tag_repository)
    mapping = {}
    for event_group in event_groups:
        chosen = random.sample(tags, random.randint(0, len(tags) // 2))
        mapping[event_group.id] = [tag.id for tag in chosen]
    await tag_repository.batch_add_tags_to_event_group(mapping)

    for event_group in event_groups:
        updated_event_group = await event_group_repository.read(event_group.id)
        assert len(updated_event_group.tags) == len(mapping[event_group.id])
        for tag in updated_event_group.tags:
            assert isinstance(tag, ViewTag)
            assert tag.id in mapping[event_group.id]
            assert tag.name in {tag.name for tag in tags}


@pytest.mark.asyncio
async def test_remove_tags_from_event_group(event_group_repository, tag_repository):
    event_group = await _create_event_group(event_group_repository)
    tag = await _create_tag(tag_repository)

    await tag_repository.add_tags_to_event_group(event_group.id, [tag.id])
    updated_event_group = await event_group_repository.read(event_group.id)
    assert len(updated_event_group.tags) == 1
    assert updated_event_group.tags[0].id == tag.id

    await tag_repository.remove_tags_from_event_group(event_group.id, [tag.id])
    updated_event_group = await event_group_repository.read(event_group.id)
    assert len(updated_event_group.tags) == 0
