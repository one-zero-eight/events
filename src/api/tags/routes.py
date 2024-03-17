from pydantic import BaseModel

from src.api.tags import router
from src.repositories.tags.repository import tag_repository
from src.schemas import ViewTag


class ListTagsResponse(BaseModel):
    tags: list[ViewTag]


@router.get(
    "/",
    responses={
        200: {"description": "List of event groups", "model": ListTagsResponse},
    },
)
async def list_tags() -> ListTagsResponse:
    """
    Get a list of all tags
    """
    tags = await tag_repository.read_all()
    return ListTagsResponse(tags=tags)
