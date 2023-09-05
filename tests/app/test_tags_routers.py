import httpx
import pytest

from src.utils import setup_repositories
from tests.repositories.test_tags import get_fake_tag


async def create_tag(tag_repository):
    await setup_repositories()
    tag_schema = get_fake_tag()
    tag = await tag_repository.create_or_read(tag_schema)
    return tag


@pytest.mark.asyncio
async def test_list_tags(async_client: httpx.AsyncClient, tag_repository):
    tags = []
    tags_number = 10
    for i in range(tags_number):
        tag = await create_tag(tag_repository)
        tags.append(tag)
    response = await async_client.get("tags/")
    response_from_api = response.json()
    assert response.status_code == 200
    for i in range(tags_number):
        assert response_from_api["tags"][i]["id"] == tags[i].id
        assert response_from_api["tags"][i]["alias"] == tags[i].alias
        assert response_from_api["tags"][i]["type"] == tags[i].type
        assert response_from_api["tags"][i]["name"] == tags[i].name
        # assert len(response_from_api["tags"][i]["ownerships"]) == 0
