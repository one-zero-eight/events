from fastapi import APIRouter
from fastapi import Body
from pydantic import BaseModel

from src.api.dependencies import VERIFY_PARSER_DEPENDENCY
from src.exceptions import IncorrectCredentialsException
from src.modules.tags.repository import tag_repository
from src.modules.tags.schemas import ViewTag, CreateTag

router = APIRouter(prefix="/tags", tags=["Tags"])


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


@router.post(
    "/batch-create-or-read",
    responses={
        200: {"description": "List of created or existing tags", "model": ListTagsResponse},
        **IncorrectCredentialsException.responses,
    },
)
async def batch_create_tags(_: VERIFY_PARSER_DEPENDENCY, tags: list[CreateTag] = Body(embed=True)) -> ListTagsResponse:
    """
    Create tags in batch
    """
    created_tags = await tag_repository.batch_create_or_read(tags)
    return ListTagsResponse(tags=created_tags)
