import aiofiles
from fastapi import UploadFile, HTTPException
from starlette.responses import FileResponse, JSONResponse

from src.app.dependencies import EVENT_GROUP_REPOSITORY_DEPENDENCY, CURRENT_USER_ID_DEPENDENCY
from src.app.event_groups import router
from src.exceptions import (
    EventGroupNotFoundException,
    OperationIsNotAllowed,
    EventGroupWithMissingPath,
    IcsFileIsNotModified,
    IncorrectCredentialsException,
    NoCredentialsException,
)
from src.repositories.predefined.repository import PredefinedRepository
from src.schemas import ViewEventGroup, ListEventGroupsResponse, CreateEventGroup, UpdateEventGroup, OwnershipEnum


@router.post(
    "/",
    responses={
        201: {"description": "Event group created successfully", "model": ViewEventGroup},
        **IncorrectCredentialsException.responses,
        **NoCredentialsException.responses,
    },
    status_code=201,
)
async def create_event_group(
    event_group: CreateEventGroup,
    event_group_repository: EVENT_GROUP_REPOSITORY_DEPENDENCY,
    current_user_id: CURRENT_USER_ID_DEPENDENCY,
) -> ViewEventGroup:
    created = await event_group_repository.create_or_update(event_group)
    await event_group_repository.setup_ownership(created.id, current_user_id, OwnershipEnum.owner)
    return created


@router.put(
    "/{event_group_id}",
    responses={
        200: {"description": "Event group updated successfully", "model": ViewEventGroup},
        **EventGroupNotFoundException.responses,
        **OperationIsNotAllowed.responses,
        **IncorrectCredentialsException.responses,
        **NoCredentialsException.responses,
    },
)
async def update_event_group(
    event_group_id: int,
    update_scheme: UpdateEventGroup,
    event_group_repository: EVENT_GROUP_REPOSITORY_DEPENDENCY,
    current_user_id: CURRENT_USER_ID_DEPENDENCY,
) -> ViewEventGroup:
    event_group = await event_group_repository.read(event_group_id)
    if event_group is None:
        raise EventGroupNotFoundException()
    owners_and_moderators = {ownership.user_id for ownership in event_group.ownerships}

    if current_user_id not in owners_and_moderators:
        raise OperationIsNotAllowed()

    event_group = await event_group_repository.update(event_group_id, update_scheme)
    return event_group


@router.get(
    "/by-path",
    responses={
        200: {"description": "Event group info", "model": ViewEventGroup},
        **EventGroupNotFoundException.responses,
    },
)
async def find_event_group_by_path(
    path: str,
    event_group_repository: EVENT_GROUP_REPOSITORY_DEPENDENCY,
) -> ViewEventGroup:
    """
    Get event group info by path
    """

    event_group = await event_group_repository.read_by_path(path)

    if event_group is None:
        raise EventGroupNotFoundException()
    return event_group


@router.get(
    "/by-alias",
    responses={
        200: {"description": "Event group info", "model": ViewEventGroup},
        **EventGroupNotFoundException.responses,
    },
)
async def find_event_group_by_alias(
    alias: str,
    event_group_repository: EVENT_GROUP_REPOSITORY_DEPENDENCY,
) -> ViewEventGroup:
    """
    Get event group info by alias
    """

    event_group = await event_group_repository.read_by_alias(alias)

    if event_group is None:
        raise EventGroupNotFoundException()
    return event_group


@router.get(
    "/{event_group_id}",
    responses={
        200: {"description": "Event group info", "model": ViewEventGroup},
        **EventGroupNotFoundException.responses,
    },
)
async def get_event_group(
    event_group_id: int,
    event_group_repository: EVENT_GROUP_REPOSITORY_DEPENDENCY,
) -> ViewEventGroup:
    """
    Get event group info by id
    """
    event_group = await event_group_repository.read(event_group_id)

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
    groups = await event_group_repository.read_all()
    return ListEventGroupsResponse.from_iterable(groups)


# ------------------ ICS-related ------------------- #
@router.put(
    "/{event_group_id}/ics",
    responses={
        201: {"description": ".ics file updated successfully"},
        # 304: {"description": ".ics file already exists and content is the same"},
        **EventGroupWithMissingPath.responses,
        **OperationIsNotAllowed.responses,
        **EventGroupNotFoundException.responses,
    },
    status_code=201,
)
async def set_event_group_ics(
    event_group_id: int,
    ics_file: UploadFile,
    event_group_repository: EVENT_GROUP_REPOSITORY_DEPENDENCY,
    current_user_id: CURRENT_USER_ID_DEPENDENCY,
):
    """
    Load .ics file to event group by event group id and save file to predefined path
    """

    event_group = await event_group_repository.read(event_group_id)

    if event_group is None:
        raise EventGroupNotFoundException()

    if event_group.path is None:
        raise EventGroupWithMissingPath()

    owners_and_moderators = {ownership.user_id for ownership in event_group.ownerships}

    if current_user_id not in owners_and_moderators:
        raise OperationIsNotAllowed()

    ics_path = PredefinedRepository.locate_ics_by_path(event_group.path)

    # TODO: add validation for ics file(return 400 if file is not valid)
    if False:
        return JSONResponse(status_code=400, content={"message": "File is not valid"})
    # TODO: compare ics files if one already exists and return 200 if they are the same
    if False:
        return IcsFileIsNotModified()

    async with aiofiles.open(ics_path, "wb") as f:
        content = await ics_file.read()
        await f.write(content)

    return JSONResponse(status_code=201, content={"message": "File uploaded successfully"})


@router.get(
    "/{event_group_id}/ics",
    response_class=FileResponse,
    responses={
        200: {
            "description": "ICS file with schedule of the event-group",
            "content": {"text/calendar": {"schema": {"type": "string", "format": "binary"}}},
        },
        **EventGroupNotFoundException.responses,
    },
)
async def get_event_group_ics(event_group_id: int, event_group_repository: EVENT_GROUP_REPOSITORY_DEPENDENCY):
    """
    Get event group .ics file by id
    """
    event_group = await event_group_repository.read(event_group_id)

    if event_group is None:
        raise EventGroupNotFoundException()
    if event_group.path:
        ics_path = PredefinedRepository.locate_ics_by_path(event_group.path)
        return FileResponse(ics_path, media_type="text/calendar")
    else:
        # TODO: create ics file on the fly from events connected to event group
        raise HTTPException(
            status_code=501, detail="Can not create .ics file on the fly (set static .ics file for the event group"
        )


@router.get(
    "/ics/{event_group_alias}.ics",
    response_class=FileResponse,
    responses={
        200: {
            "description": "ICS file with schedule of the event-group",
            "content": {"text/calendar": {"schema": {"type": "string", "format": "binary"}}},
        },
        **EventGroupNotFoundException.responses,
    },
)
async def get_event_group_ics_by_alias(
    event_group_alias: str, event_group_repository: EVENT_GROUP_REPOSITORY_DEPENDENCY
):
    """
    Get event group .ics file by id
    """
    event_group = await event_group_repository.read_by_alias(event_group_alias)

    if event_group is None:
        raise EventGroupNotFoundException()
    if event_group.path:
        ics_path = PredefinedRepository.locate_ics_by_path(event_group.path)
        return FileResponse(ics_path, media_type="text/calendar")
    else:
        # TODO: create ics file on the fly from events connected to event group
        raise HTTPException(
            status_code=501, detail="Can not create .ics file on the fly (set static .ics file for the event group"
        )


# ^^^^^^^^^^^^^ ICS-related ^^^^^^^^^^^^^^^^^^^^^^^^ #
