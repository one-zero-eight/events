from typing import Annotated

import pytest
from faker import Faker
from fastapi import FastAPI, Depends
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


@pytest.fixture(scope="function")
async def fake_app(monkeypatch, fake_predefined_repository):
    class FakePredefinedGroupsRepository:
        @classmethod
        def from_files(cls, *args, **kwargs):
            return fake_predefined_repository

    monkeypatch.setattr(
        "src.repositories.users.json_repository.PredefinedGroupsRepository", FakePredefinedGroupsRepository
    )

    from src.main import app

    assert isinstance(app, FastAPI)

    return app


@pytest.mark.asyncio
async def test_app_configuration(fake_app):
    fake_app = await fake_app
    with TestClient(fake_app):
        ...


@pytest.fixture
def mock_event_group_repository():
    from src.schemas.event_groups import ViewEventGroup

    class MockEventGroupRepository:
        async def get_group_by_path(self, path):
            if path == "/existing-path":
                return ViewEventGroup(id=1, name="Existing Event Group", path="/existing-path")
            return None

        async def get_group(self, event_group_id):
            if event_group_id == 1:
                return ViewEventGroup(id=1, name="Existing Event Group", path="/existing-path")
            return None

        async def get_all_groups(self):
            return [
                ViewEventGroup(id=1, name="Existing Event Group", path="/existing-path"),
                ViewEventGroup(id=2, name="Existing Event Group 2", path="/existing-path-2"),
            ]

    return MockEventGroupRepository()


@pytest.fixture(scope="function", autouse=True)
def override_dependencies(monkeypatch, mock_event_group_repository):
    from src.repositories.event_groups import AbstractEventGroupRepository

    new_dependency = Annotated[AbstractEventGroupRepository, Depends(lambda: mock_event_group_repository)]
    monkeypatch.setattr("src.app.dependencies.EVENT_GROUP_REPOSITORY_DEPENDENCY", new_dependency)


@pytest.mark.asyncio
async def test_find_event_group_by_path(fake_app):
    app = await fake_app

    with TestClient(app) as client:
        response = client.get("/event-groups/by-path?path=/existing-path")

        assert response.status_code == 200
        assert response.json() is not None

        response = client.get("/by-path?path=/non-existing-path")
        assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_event_group(fake_app):
    app = await fake_app

    with TestClient(app) as client:
        response = client.get("/event-groups/1")

        assert response.status_code == 200
        assert response.json() is not None

        response = client.get("/event-groups/2")
        assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_all_event_groups(fake_app):
    app = await fake_app

    with TestClient(app) as client:
        response = client.get("/event-groups")

        assert response.status_code == 200
        assert response.json() is not None
        assert len(response.json()) > 0
