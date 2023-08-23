import random
from pathlib import Path

import pytest
from faker import Faker
from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.main import app
from src.repositories.predefined.repository import (
    JsonGroupStorage,
    JsonUserStorage,
    JsonTagStorage,
)

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

    monkeysession.setattr(settings, "PREDEFINED_DIR", Path("tests/repositories/temp/predefined"))

    # ensure directory exists
    settings.PREDEFINED_DIR.mkdir(parents=True, exist_ok=True)


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
            alias=group.alias,
            description=group.description,
            name=group.name,  # path=group.path
        )
        predefined_groups.append(predefined_group)

    user_storage = JsonUserStorage(users=fake_users)
    group_storage = JsonGroupStorage(event_groups=predefined_groups)
    tag_storage = JsonTagStorage(tags=[fake_tag() for _ in range(10)])

    # save to file
    from src.config import settings

    with (
        (settings.PREDEFINED_DIR / "innopolis_user_data.json").open("w", encoding="utf-8") as users_file,
        (settings.PREDEFINED_DIR / "predefined_event_groups.json").open("w", encoding="utf-8") as groups_file,
        (settings.PREDEFINED_DIR / "predefined_tags.json").open("w", encoding="utf-8") as tags_file,
    ):
        users_file.write(user_storage.json())
        groups_file.write(group_storage.json())
        tags_file.write(tag_storage.json())

    # TODO: Generate iCal files


@pytest.mark.asyncio
async def test_startup():
    assert isinstance(app, FastAPI)

    with TestClient(app):
        ...
