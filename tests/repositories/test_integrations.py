import random

import pytest
from faker import Faker

from src.schemas import ViewTag
from src.schemas.event_groups import UserXFavoriteGroupView
from src.schemas.users import ViewUser
from tests.repositories.test_event_groups import _create_event_group, _batch_create_event_group
from tests.repositories.test_tags import _create_tag, _batch_create_tag
from tests.repositories.test_users import _create_user, _batch_create_user_if_not_exists

fake = Faker()


# ------------- User x Event Group ------------- #
@pytest.mark.asyncio
async def test_setup_groups(event_group_repository, user_repository):
    user = await _create_user(user_repository)
    event_group = await _create_event_group(event_group_repository)
    await event_group_repository.setup_groups(user.id, [event_group.id])

    updated_user = await user_repository.read(user.id)
    user_x_group = updated_user.favorites_association[0]
    assert isinstance(user_x_group, UserXFavoriteGroupView)
    assert user_x_group.predefined is True
    assert user_x_group.user_id == user.id
    assert user_x_group.event_group.id == event_group.id


@pytest.mark.asyncio
async def test_batch_setup_groups(event_group_repository, user_repository):
    users = await _batch_create_user_if_not_exists(user_repository)
    event_groups = await _batch_create_event_group(event_group_repository)
    # random mapping
    mapping = {
        user.id: random.sample([event_group.id for event_group in event_groups], random.randint(1, 5)) for user in users
    }
    await event_group_repository.batch_setup_groups(mapping)
    updated_users = await user_repository.batch_read([user.id for user in users])
    for updated_user in updated_users:
        assert isinstance(updated_user, ViewUser)
        assert len(updated_user.favorites_association) in [1, 2, 3, 4, 5]
        for user_x_group in updated_user.favorites_association:
            assert isinstance(user_x_group, UserXFavoriteGroupView)
            assert user_x_group.predefined is True
            assert user_x_group.user_id == updated_user.id
            assert user_x_group.event_group.id in mapping[updated_user.id]


@pytest.mark.asyncio
async def test_set_hidden(event_group_repository, user_repository):
    user = await _create_user(user_repository)
    event_group = await _create_event_group(event_group_repository)

    await event_group_repository.setup_groups(user.id, [event_group.id])

    updated_user = await user_repository.read(user.id)
    user_x_group = updated_user.favorites_association[0]
    assert isinstance(user_x_group, UserXFavoriteGroupView)
    assert user_x_group.user_id == user.id
    assert user_x_group.event_group.id == event_group.id
    assert user_x_group.hidden is False

    await user_repository.set_hidden_event_group(user.id, event_group.id, True)
    updated_user = await user_repository.read(user.id)
    user_x_group = updated_user.favorites_association[0]
    assert user_x_group.hidden is True


@pytest.mark.asyncio
async def test_add_favorite(event_group_repository, user_repository):
    user = await _create_user(user_repository)
    event_group = await _create_event_group(event_group_repository)

    updated_user = await user_repository.add_favorite(user.id, event_group.id)
    user_x_group = updated_user.favorites_association[0]
    assert isinstance(user_x_group, UserXFavoriteGroupView)
    assert user_x_group.user_id == user.id
    assert user_x_group.event_group.id == event_group.id
    assert user_x_group.predefined is False


@pytest.mark.asyncio
async def test_add_favorite_with_wrong_group(event_group_repository, user_repository):
    from src.exceptions import DBEventGroupDoesNotExistInDb

    user = await _create_user(user_repository)
    NOT_EXISTING_GROUP_ID = 1
    with pytest.raises(DBEventGroupDoesNotExistInDb):
        await user_repository.add_favorite(user.id, NOT_EXISTING_GROUP_ID)


@pytest.mark.asyncio
async def test_remove_favorite(event_group_repository, user_repository):
    user = await _create_user(user_repository)
    event_group = await _create_event_group(event_group_repository)

    await user_repository.add_favorite(user.id, event_group.id)

    updated_user = await user_repository.remove_favorite(user.id, event_group.id)
    assert len(updated_user.favorites_association) == 0


# ^^^^^^^^^^^^^^^^^ User x Event Group ^^^^^^^^^^^^^^^^^ #
# ------------- Event Group x Tag ------------- #


@pytest.mark.asyncio
async def test_add_tags_to_event_group(event_group_repository, tag_repository):
    event_group = await _create_event_group(event_group_repository)
    tags = await _batch_create_tag(tag_repository)
    await tag_repository.add_tags_to_event_group(event_group.id, [tag.id for tag in tags])

    updated_event_group = await event_group_repository.read(event_group.id)
    assert len(updated_event_group.tags) == len(tags)
    for tag in updated_event_group.tags:
        assert isinstance(tag, ViewTag)
        assert tag.id in {tag.id for tag in tags}


@pytest.mark.asyncio
async def test_batch_add_tags_to_event_group(event_group_repository, tag_repository):
    event_groups = await _batch_create_event_group(event_group_repository)
    tags = await _batch_create_tag(tag_repository)
    mapping = {}
    for event_group in event_groups:
        chosen = random.sample(tags, random.randint(0, len(tags) // 2))
        mapping[event_group.id] = [tag.id for tag in chosen]
    await tag_repository.batch_set_tags_to_event_group(mapping)

    for event_group in event_groups:
        updated_event_group = await event_group_repository.read(event_group.id)
        assert len(updated_event_group.tags) == len(mapping[event_group.id])
        for tag in updated_event_group.tags:
            assert isinstance(tag, ViewTag)
            assert tag.id in mapping[event_group.id]


@pytest.mark.asyncio
async def test_remove_tags_from_event_group(event_group_repository, tag_repository):
    event_group = await _create_event_group(event_group_repository)
    tag = await _create_tag(tag_repository)

    await tag_repository.add_tags_to_event_group(event_group.id, [tag.id])
    updated_event_group = await event_group_repository.read(event_group.id)
    assert updated_event_group.tags[0].id == tag.id

    await tag_repository.remove_tags_from_event_group(event_group.id, [tag.id])
    updated_event_group = await event_group_repository.read(event_group.id)
    assert len(updated_event_group.tags) == 0


# ^^^^^^^^^^^^^^^^^ Event Group x Tag ^^^^^^^^^^^^^^^^^ #
