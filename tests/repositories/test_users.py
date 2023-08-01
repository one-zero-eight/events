import pytest
from faker import Faker

from src.schemas.users import CreateUser, ViewUser

fake = Faker()


def get_fake_user() -> CreateUser:
    return CreateUser(email=fake.email(), name=fake.name())


async def _create_user(user_repository) -> "ViewUser":
    user_schema = get_fake_user()
    user = await user_repository.create_or_read(user_schema)
    assert user is not None
    assert isinstance(user, ViewUser)
    assert user.id is not None
    assert user.email == user_schema.email
    assert user.name == user_schema.name
    return user


async def _batch_create_user_if_not_exists(user_repository) -> list["ViewUser"]:
    # Create a batch of new users
    user_schemas = [get_fake_user() for _ in range(10)]
    users = await user_repository.batch_create_or_read(user_schemas)
    assert len(users) == len(user_schemas)
    for user, user_schema in zip(users, user_schemas):
        assert user is not None
        assert isinstance(user, ViewUser)
        assert user.id is not None
        assert user.email == user_schema.email
        assert user.name == user_schema.name

    return users


@pytest.mark.asyncio
async def test_create_if_not_exists(user_repository):
    _user = await _create_user(user_repository)


@pytest.mark.asyncio
async def test_create_existing(
    user_repository,
):
    scheme = get_fake_user()
    user = await user_repository.create_or_read(scheme)
    hit = await user_repository.create_or_read(scheme)
    assert user.id == hit.id
    assert user.email == hit.email


@pytest.mark.asyncio
async def test_batch_create_user_if_not_exists(user_repository):
    _users = await _batch_create_user_if_not_exists(user_repository)


@pytest.mark.asyncio
async def test_upsert_user(user_repository):
    # Create a new user
    user = await _create_user(user_repository)

    # Update an existing user
    updated_user_schema = CreateUser(email=user.email, name=fake.name())
    updated_user = await user_repository.create_or_update(updated_user_schema)
    assert updated_user is not None
    assert isinstance(updated_user, ViewUser)
    assert updated_user.id == user.id
    assert updated_user.email == updated_user_schema.email
    assert updated_user.name == updated_user_schema.name


@pytest.mark.asyncio
async def test_get_user_id_by_email(user_repository):
    # Create a new user
    user = await _create_user(user_repository)
    # Retrieve the user ID by email
    user_id = await user_repository.read_id_by_email(user.email)
    assert user_id is not None
    assert isinstance(user_id, int)
    assert user_id == user.id


@pytest.mark.asyncio
async def test_get_user(user_repository):
    # Create a new user
    created_user = await _create_user(user_repository)

    # Retrieve the user by ID
    retrieved_user = await user_repository.read(created_user.id)
    assert retrieved_user is not None
    assert isinstance(retrieved_user, ViewUser)
    assert retrieved_user.id == created_user.id
    assert retrieved_user.email == created_user.email
    assert retrieved_user.name == created_user.name


@pytest.mark.asyncio
async def test_batch_get_user(user_repository):
    # Create a batch of new users
    created_users = await _batch_create_user_if_not_exists(user_repository)
    # Retrieve the users by their IDs
    user_ids = [user.id for user in created_users]
    retrieved_users = await user_repository.batch_read(user_ids)
    assert len(retrieved_users) == len(created_users)
    for retrieved_user, created_user in zip(retrieved_users, created_users):
        assert retrieved_user is not None
        assert isinstance(retrieved_user, ViewUser)
        assert retrieved_user.id == created_user.id
        assert retrieved_user.email == created_user.email
        assert retrieved_user.name == created_user.name
