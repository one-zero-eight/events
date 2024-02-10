import datetime
import os
import random
from pathlib import Path

import httpx
import icalendar
import pytest
from faker import Faker

from src.repositories.predefined.repository import (
    JsonGroupStorage,
    JsonUserStorage,
    JsonTagStorage,
    CategoryStorage,
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
    settings.predefined_dir.mkdir(parents=True, exist_ok=True)


def fake_icalendar() -> icalendar.Calendar:
    calendar = icalendar.Calendar()
    calendar.add("prodid", "-//InNoHassle//EN")
    calendar.add("version", "2.0")

    events = []
    cnt = random.randint(0, 10)
    for _ in range(cnt):
        event = icalendar.Event()
        event.add("summary", fake.slug())
        dtstart = fake.date_time()
        duration = datetime.timedelta(hours=random.randint(0, 10))
        dtend = dtstart + duration
        event.add("dtstart", icalendar.vDatetime(dtstart))
        event.add("dtend", icalendar.vDatetime(dtend))
        event.add("dtstamp", fake.date_time())
        event.add("uid", fake.slug() + "@innohassle.ru")
        event.add("description", fake.text())
        event.add("location", fake.address())
        events.append(event)
    return calendar


@pytest.fixture(scope="session", autouse=True)
def fake_predefined_repository():
    # save to file
    from src.config import settings
    import json

    def fake_group() -> JsonGroupStorage.PredefinedGroup:
        path = fake.slug() + ".ics"
        return JsonGroupStorage.PredefinedGroup(alias=fake.slug(), name=fake.name(), description=fake.slug(), path=path)

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

    fake_categories = {
        "categories": [
            {"path": "category1.json"},
        ]
    }

    os.makedirs(settings.predefined_dir / "ics", exist_ok=True)

    for group in fake_groups:
        calendar = fake_icalendar()
        with (settings.predefined_dir / "ics" / f"{group.path}").open("wb") as ics_file:
            ics_file.write(calendar.to_ical())

        predefined_group = JsonGroupStorage.PredefinedGroup(
            alias=group.alias, description=group.description, name=group.name, path=group.path
        )
        predefined_groups.append(predefined_group)

    user_storage = JsonUserStorage(users=fake_users)
    tags = [fake_tag() for _ in range(10)]
    category_storage = CategoryStorage(event_groups=predefined_groups, tags=tags)

    with (
        (settings.predefined_dir / "innopolis_user_data.json").open("w", encoding="utf-8") as users_file,
        (settings.predefined_dir / "categories.json").open("w", encoding="utf-8") as categories_file,
        (settings.predefined_dir / fake_categories["categories"][0]["path"]).open(
            "w", encoding="utf-8"
        ) as category_file,
    ):
        users_file.write(user_storage.json())
        json.dump(fake_categories, categories_file)
        category_file.write(category_storage.json())


@pytest.mark.asyncio
async def test_startup(async_client: httpx.AsyncClient):
    from src.api.auth.jwt import create_parser_token

    token = create_parser_token()

    # set Bearer
    async_client.headers["Authorization"] = f"Bearer {token}"
    response = await async_client.get("/update-predefined-data")
    assert response.status_code == 200
