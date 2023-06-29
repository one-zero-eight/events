from typing import Annotated, Iterable

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from src.app.event_groups.schemas import ViewEventGroup
from src.exceptions import EventGroupNotFoundException
from src.repositories.dependencies import Dependencies
from src.repositories.users import AbstractUserRepository

router = APIRouter(prefix="/event-groups", tags=["Event Groups"])


@router.get(
    "/by-path",
    responses={
        200: {"description": "Event group info", "model": ViewEventGroup},
        404: {"description": "Event group not found"},
    },
)
async def find_event_group_by_path(
    path: str,
    user_repository: Annotated[
        AbstractUserRepository, Depends(Dependencies.get_user_repository)
    ],
) -> ViewEventGroup:
    """
    Get event group info by path
    """

    event_group = await user_repository.get_group_by_path(path)

    if event_group is None:
        raise EventGroupNotFoundException()
    return event_group


@router.get(
    "/{event_group_id}",
    responses={
        200: {"description": "Event group info", "model": ViewEventGroup},
        404: {"description": "Event group not found"},
    },
)
async def get_event_group(
    event_group_id: int,
    user_repository: Annotated[
        AbstractUserRepository, Depends(Dependencies.get_user_repository)
    ],
) -> ViewEventGroup:
    """
    Get event group info by id
    """
    event_group = await user_repository.get_group(event_group_id)

    if event_group is None:
        raise EventGroupNotFoundException()

    return event_group


class ListEventGroupsResponse(BaseModel):
    """
    Represents a list of event groups.
    """

    groups: list[ViewEventGroup]

    @classmethod
    def from_iterable(
        cls, groups: Iterable[ViewEventGroup]
    ) -> "ListEventGroupsResponse":
        return cls(groups=groups)


@router.get(
    "/",
    responses={
        200: {"description": "List of event groups", "model": ListEventGroupsResponse},
    },
)
async def list_event_groups(
    user_repository: Annotated[
        AbstractUserRepository, Depends(Dependencies.get_user_repository)
    ],
) -> ListEventGroupsResponse:
    """
    Get list of event groups
    """
    groups = await user_repository.get_all_groups()
    return ListEventGroupsResponse.from_iterable(groups)
