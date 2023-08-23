import httpx
import pytest

from src.main import setup_repositories
from tests.misc.test_nonobvious_schemas import get_fake_create_event_group


async def create_event_group(event_group_repository):
    await setup_repositories()
    event_group_schema = get_fake_create_event_group()
    event_group = await event_group_repository.create(event_group_schema)
    return event_group


@pytest.mark.asyncio
async def test_get_event_group(async_client: httpx.AsyncClient, event_group_repository):
    event_group = await create_event_group(event_group_repository)
    response = await async_client.get(f"event-groups/{event_group.id}")
    response_from_api = response.json()
    assert response.status_code == 200
    assert event_group.alias in response_from_api["alias"]
    assert event_group.id == response_from_api["id"]
    assert event_group.path in response_from_api["path"]
    assert event_group.name in response_from_api["name"]


@pytest.mark.asyncio
async def test_find_event_group_by_path(async_client: httpx.AsyncClient, event_group_repository):
    event_group = await create_event_group(event_group_repository)
    response = await async_client.get(f"event-groups/by-path?path={event_group.path}")
    assert response.status_code == 200
    response_from_api = response.json()
    assert event_group.alias in response_from_api["alias"]
    assert event_group.id == response_from_api["id"]
    assert event_group.path in response_from_api["path"]
    assert event_group.name in response_from_api["name"]


@pytest.mark.asyncio
async def test_not_find_event_group_by_path(async_client: httpx.AsyncClient, event_group_repository):
    await setup_repositories()
    response = await async_client.get("event-groups/by-path?path=nonexistingpath")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_list_event_groups(async_client: httpx.AsyncClient, event_group_repository):
    event_groups = []
    event_groups_number = 10
    for i in range(event_groups_number):
        event_group = await create_event_group(event_group_repository)
        event_groups.append(event_group)
    response = await async_client.get("event-groups/")
    response_from_api = response.json()
    assert response.status_code == 200

    for i in range(event_groups_number):
        assert response_from_api["groups"][i]["alias"] == event_groups[i].alias
        assert response_from_api["groups"][i]["name"] == event_groups[i].name
        assert response_from_api["groups"][i]["path"] == event_groups[i].path
        assert response_from_api["groups"][i]["description"] == event_groups[i].description
        assert len(response_from_api["groups"][i]["ownerships"]) == 0
        assert len(response_from_api["groups"][i]["tags"]) == 0
