from pydantic import BaseModel

from src.app.dependencies import Shared
from src.app.tags import router
from src.repositories.tags import SqlTagRepository
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
    tag_repository = Shared.f(SqlTagRepository)
    tags = await tag_repository.read_all()
    return ListTagsResponse(tags=tags)
