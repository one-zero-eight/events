import pytest
from faker import Faker
from fastapi import FastAPI
from fastapi.testclient import TestClient

fake = Faker()


@pytest.fixture(scope="session")
def fake_predefined_repository():
    from src.repositories.users.json_repository import InJsonUser, InJsonEventGroup, JsonUserStorage, JsonGroupStorage
    from src.repositories.users.json_repository import PredefinedGroup, PredefinedGroupsRepository

    def fake_group() -> InJsonEventGroup:
        return InJsonEventGroup(name=fake.name(), type=fake.slug(), path=fake.slug())

    def fake_user():
        return InJsonUser(email=fake.email(), groups=[fake_group(), fake_group()])

    fake_users = [fake_user() for _ in range(10)]
    groups = list()
    chosen_groups = set()

    for user in fake_users:
        for group in user.groups:
            if group.path not in chosen_groups:
                chosen_groups.add(group.path)
                groups.append(group)

    predefined_groups = []
    for group in groups:
        predefined_group = PredefinedGroup(name=group.name, type=group.type, path=group.path, satellite=None)
        predefined_groups.append(predefined_group)

    user_storage = JsonUserStorage(users=fake_users)
    group_storage = JsonGroupStorage(groups=predefined_groups)

    repository = PredefinedGroupsRepository(user_storage, group_storage)

    return repository


@pytest.mark.asyncio
async def test_startup(monkeypatch, fake_predefined_repository):
    class FakePredefinedGroupsRepository:
        @classmethod
        def from_files(cls, *args, **kwargs):
            return fake_predefined_repository

    monkeypatch.setattr(
        "src.repositories.users.json_repository.PredefinedGroupsRepository", FakePredefinedGroupsRepository
    )

    from src.main import app

    assert isinstance(app, FastAPI)

    with TestClient(app):
        ...
