from pydantic import BaseModel

from src.app.dependencies import TAG_REPOSITORY_DEPENDENCY
from src.app.tags import router
from src.schemas import ViewTag


class ListTagsResponse(BaseModel):
    tags: list[ViewTag]


@router.get(
    "/",
    responses={
        200: {"description": "List of event groups", "model": ListTagsResponse},
    },
)
async def list_tags(
    tag_repository: TAG_REPOSITORY_DEPENDENCY,
) -> ListTagsResponse:
    """
    Get a list of all tags
    """
    tags = await tag_repository.read_all()
    return ListTagsResponse(tags=tags)
