import pytest
from faker import Faker
from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.repositories.predefined.repository import (
    PredefinedRepository,
    JsonGroupStorage,
    JsonUserStorage,
    JsonTagStorage,
)

fake = Faker()


@pytest.fixture(scope="session")
def fake_predefined_repository():
    def fake_group() -> JsonGroupStorage.PredefinedGroup:
        return JsonGroupStorage.PredefinedGroup(name=fake.name(), description=fake.slug(), path=fake.slug())

    def fake_tag() -> JsonTagStorage.Tag:
        return JsonTagStorage.Tag(alias=fake.slug(), name=fake.slug(), type=fake.slug())

    def fake_user() -> JsonUserStorage.InJsonUser:
        return JsonUserStorage.InJsonUser(email=fake.email(), groups=[fake_group(), fake_group()])

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
        predefined_group = JsonGroupStorage.PredefinedGroup(name=group.name, path=group.path)
        predefined_groups.append(predefined_group)

    user_storage = JsonUserStorage(users=fake_users)
    group_storage = JsonGroupStorage(event_groups=predefined_groups)
    tag_storage = JsonTagStorage(tags=[fake_tag() for _ in range(10)])

    repository = PredefinedRepository(user_storage, group_storage, tag_storage)

    return repository


@pytest.fixture(scope="function", autouse=True)
def fake_predefined_repository_function(monkeypatch, fake_predefined_repository):
    class FakePredefinedGroupsRepository:
        @classmethod
        def from_jsons(cls, *_, **__):
            return fake_predefined_repository

    monkeypatch.setattr(PredefinedRepository, "from_jsons", FakePredefinedGroupsRepository.from_jsons)


@pytest.mark.asyncio
async def test_startup():
    from src.main import app

    assert isinstance(app, FastAPI)

    with TestClient(app):
        ...
