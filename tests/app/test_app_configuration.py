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

fake = Faker()


@pytest.fixture(scope="session")
def monkeymodule():
    from _pytest.monkeypatch import MonkeyPatch

    mpatch = MonkeyPatch()
    yield mpatch
    mpatch.undo()


@pytest.fixture(scope="session", autouse=True)
def fake_paths(monkeymodule):
    from src.config import settings

    monkeymodule.setattr(settings, "PREDEFINED_GROUPS_FILE", Path("tests/repositories/temp/test_groups.json.tmp"))
    monkeymodule.setattr(settings, "PREDEFINED_TAGS_FILE", Path("tests/repositories/temp/test_tags.json.tmp"))
    monkeymodule.setattr(settings, "PREDEFINED_USERS_FILE", Path("tests/repositories/temp/test_users.json.tmp"))


@pytest.fixture(scope="session", autouse=True)
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
    from src.main import app

    assert isinstance(app, FastAPI)

    with TestClient(app):
        ...
