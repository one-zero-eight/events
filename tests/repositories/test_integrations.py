import random
from typing import TYPE_CHECKING

import pytest
from faker import Faker

from src.schemas.event_groups import UserXFavoriteGroupView
from src.schemas.users import ViewUser
from tests.repositories.test_event_groups import _create_event_group, _batch_create_event_group
from tests.repositories.test_users import _create_user, _batch_create_user_if_not_exists

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
