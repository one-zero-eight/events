from src.app.dependencies import EVENT_GROUP_REPOSITORY_DEPENDENCY, IS_VERIFIED_PARSER_DEPENDENCY
from src.app.event_groups import router
from src.schemas.event_groups import CreateEventGroup, ViewEventGroup, ListEventGroupsResponse
from src.exceptions import EventGroupNotFoundException


@router.get(
    "/by-path",
    responses={
        200: {"description": "Event group info", "model": ViewEventGroup},
        404: {"description": "Event group not found"},
    },
)
async def find_event_group_by_path(
    path: str,
    event_group_repository: EVENT_GROUP_REPOSITORY_DEPENDENCY,
) -> ViewEventGroup:
    """
    Get event group info by path
    """

    event_group = await event_group_repository.get_group_by_path(path)

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
    event_group_repository: EVENT_GROUP_REPOSITORY_DEPENDENCY,
) -> ViewEventGroup:
    """
    Get event group info by id
    """
    event_group = await event_group_repository.get_group(event_group_id)

    if event_group is None:
        raise EventGroupNotFoundException()

    return event_group


@router.get(
    "/",
    responses={
        200: {"description": "List of event groups", "model": ListEventGroupsResponse},
    },
)
async def list_event_groups(
    event_group_repository: EVENT_GROUP_REPOSITORY_DEPENDENCY,
) -> ListEventGroupsResponse:
    """
    Get a list of all event groups
    """
    groups = await event_group_repository.get_all_groups()
    return ListEventGroupsResponse.from_iterable(groups)


@router.post(
    "/",
    responses={
        200: {"description": "Event group info", "model": ViewEventGroup},
        401: {"description": "No credentials provided"},
        403: {"description": "Could not validate credentials"},
    },
)
async def create_event_group(
    _is_verified: IS_VERIFIED_PARSER_DEPENDENCY,
    event_group_repository: EVENT_GROUP_REPOSITORY_DEPENDENCY,
    event_group: CreateEventGroup,
) -> ViewEventGroup:
    """
    Create a new event group if it does not exist
    """
    return await event_group_repository.create_group_if_not_exists(event_group)
