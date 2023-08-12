import random
from pathlib import Path

import pytest
from faker import Faker
from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.repositories.predefined.repository import (
    JsonGroupStorage,
    JsonUserStorage,
    JsonTagStorage,
)

from src.main import app
from src.main import settings

fake = Faker()


@pytest.fixture(scope="session")
def monkeysession():
    from _pytest.monkeypatch import MonkeyPatch

    mpatch = MonkeyPatch()
    yield mpatch
    mpatch.undo()


@pytest.fixture(scope="session", autouse=True)
def fake_paths(monkeysession):
    from src.config import settings

    monkeysession.setattr(settings, "PREDEFINED_GROUPS_FILE", Path("tests/repositories/temp/test_groups.json.tmp"))
    monkeysession.setattr(settings, "PREDEFINED_TAGS_FILE", Path("tests/repositories/temp/test_tags.json.tmp"))
    monkeysession.setattr(settings, "PREDEFINED_USERS_FILE", Path("tests/repositories/temp/test_users.json.tmp"))

    # ensure directory exists
    settings.PREDEFINED_GROUPS_FILE.parent.mkdir(parents=True, exist_ok=True)


@pytest.fixture(scope="session", autouse=True)
def fake_predefined_repository():
    def fake_group() -> JsonGroupStorage.PredefinedGroup:
        return JsonGroupStorage.PredefinedGroup(
            alias=fake.slug(), name=fake.name(), description=fake.slug(), path=fake.slug()
        )

    def fake_tag() -> JsonTagStorage.Tag:
        return JsonTagStorage.Tag(alias=fake.slug(), name=fake.slug(), type=fake.slug())

    def fake_user() -> JsonUserStorage.InJsonUser:
        return JsonUserStorage.InJsonUser(email=fake.email())

    fake_users = [fake_user() for _ in range(10)]
    fake_groups = [fake_group() for _ in range(20)]

    for user in fake_users:
        groups_to_add = random.sample(fake_groups, random.randint(0, 5))
        user.groups = [group.alias for group in groups_to_add]

    predefined_groups = []
    for group in fake_groups:
        predefined_group = JsonGroupStorage.PredefinedGroup(
            alias=group.alias, description=group.description, name=group.name, path=group.path
        )
        predefined_groups.append(predefined_group)

    user_storage = JsonUserStorage(users=fake_users)
    group_storage = JsonGroupStorage(event_groups=predefined_groups)
    tag_storage = JsonTagStorage(tags=[fake_tag() for _ in range(10)])

    # save to file
    from src.config import settings

    with (
        settings.PREDEFINED_GROUPS_FILE.open("w", encoding="utf-8") as groups_file,
        settings.PREDEFINED_TAGS_FILE.open("w", encoding="utf-8") as tags_file,
        settings.PREDEFINED_USERS_FILE.open("w", encoding="utf-8") as users_file,
    ):
        groups_file.write(group_storage.json())
        tags_file.write(tag_storage.json())
        users_file.write(user_storage.json())


@pytest.mark.asyncio
async def test_startup():
    assert isinstance(app, FastAPI)

    with TestClient(app):
        ...


def test_version():
    client = TestClient(app)

    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {
        "title": settings.APP_TITLE,
        "description": settings.APP_DESCRIPTION,
        "version": settings.APP_VERSION,
    }
