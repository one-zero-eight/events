import aiofiles
import icalendar
from fastapi import UploadFile, HTTPException, Body
from sqlalchemy.exc import IntegrityError
from starlette.responses import JSONResponse

from src.api.dependencies import (
    VERIFY_PARSER_DEPENDENCY,
)
from src.api.event_groups import router
from src.api.ics.utils import locate_ics_by_path
from src.exceptions import (
    EventGroupNotFoundException,
    EventGroupWithMissingPath,
    IncorrectCredentialsException,
    NoCredentialsException,
    ForbiddenException,
)
from src.repositories.event_groups.repository import event_group_repository
from src.schemas import ViewEventGroup, ListEventGroupsResponse, CreateEventGroup, UpdateEventGroup


@router.post(
    "/",
    responses={
        201: {"description": "Event group created successfully", "model": ViewEventGroup},
        409: {"description": "Integrity error, unique constraint violation. Return existing event group"},
        **IncorrectCredentialsException.responses,
        **NoCredentialsException.responses,
    },
    status_code=201,
)
async def create_event_group(
    event_group: CreateEventGroup,
    # current_user_id: CURRENT_USER_ID_DEPENDENCY,
    _: VERIFY_PARSER_DEPENDENCY,
):
    try:
        event_group_view = await event_group_repository.create(event_group)
        # await event_group_repository.setup_ownership(event_group_view.id, current_user_id, OwnershipEnum.owner)
        return JSONResponse(status_code=201, content=event_group_view.model_dump())
    except IntegrityError as integrity_error:
        detail = integrity_error.args[0]
        raise HTTPException(status_code=409, detail=detail)


@router.post(
    "/batch-create-or-read",
    responses={
        201: {"description": "List of created or existing event groups", "model": ListEventGroupsResponse},
        **IncorrectCredentialsException.responses,
        **NoCredentialsException.responses,
    },
    status_code=201,
)
async def batch_create_event_groups(
    # current_user_id: CURRENT_USER_ID_DEPENDENCY,
    _: VERIFY_PARSER_DEPENDENCY,
    event_groups: list[CreateEventGroup] = Body(embed=True),
) -> ListEventGroupsResponse:
    created_groups = await event_group_repository.batch_create_or_read(event_groups)
    return ListEventGroupsResponse.from_iterable(created_groups)


@router.put(
    "/{event_group_id}",
    responses={
        200: {"description": "Event group updated successfully", "model": ViewEventGroup},
        **EventGroupNotFoundException.responses,
        **ForbiddenException.responses,
        **IncorrectCredentialsException.responses,
        **NoCredentialsException.responses,
    },
)
async def update_event_group(
    event_group_id: int,
    update_scheme: UpdateEventGroup,
    # current_user_id: CURRENT_USER_ID_DEPENDENCY,
    _: VERIFY_PARSER_DEPENDENCY,
) -> ViewEventGroup:
    event_group = await event_group_repository.read(event_group_id)

    if event_group is None:
        raise EventGroupNotFoundException()

    # owners_and_moderators = {ownership.user_id for ownership in event_group.ownerships}
    #
    # if current_user_id not in owners_and_moderators:
    #     raise OperationIsNotAllowed()

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
) -> ViewEventGroup:
    """
    Get event group info by alias
    """

    event_group = await event_group_repository.read_by_alias(alias)

    if event_group is None:
        raise EventGroupNotFoundException()
    return event_group


@router.delete(
    "/by-alias",
    responses={
        200: {"description": "Event group deleted successfully"},
        **EventGroupNotFoundException.responses,
    },
)
async def delete_event_group_by_alias(
    alias: str,
) -> None:
    """
    Delete event group by alias
    """

    event_group = await event_group_repository.read_by_alias(alias)

    if event_group is None:
        raise EventGroupNotFoundException()

    await event_group_repository.delete_by_alias(alias)


@router.get(
    "/{event_group_id}",
    responses={
        200: {"description": "Event group info", "model": ViewEventGroup},
        **EventGroupNotFoundException.responses,
    },
)
async def get_event_group(
    event_group_id: int,
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
async def list_event_groups() -> ListEventGroupsResponse:
    """
    Get a list of all event groups
    """

    groups = await event_group_repository.read_all()
    return ListEventGroupsResponse.from_iterable(groups)


# ------------------ ICS-related ------------------- #


@router.put(
    "/{event_group_id}/schedule.ics",
    responses={
        200: {"description": ".ics file is not modified"},
        201: {"description": ".ics file updated successfully"},
        # 304: {"description": ".ics file already exists and content is the same"},
        **EventGroupWithMissingPath.responses,
        **EventGroupNotFoundException.responses,
        **IncorrectCredentialsException.responses,
        **NoCredentialsException.responses,
    },
    status_code=201,
    tags=["ICS"],
)
async def set_event_group_ics(
    event_group_id: int,
    ics_file: UploadFile,
    # current_user_id: CURRENT_USER_ID_DEPENDENCY,
    _: VERIFY_PARSER_DEPENDENCY,
):
    """
    Load .ics file to event group by event group id and save file to predefined path
    """
    if ics_file.content_type != "text/calendar":
        return JSONResponse(
            status_code=400,
            content={"detail": f"File content type is {ics_file.content_type}, but should be 'text/calendar'"},
        )

    event_group_path = await event_group_repository.get_only_path(event_group_id)

    if event_group_path is None:
        raise EventGroupWithMissingPath()

    # owners_and_moderators = {ownership.user_id for ownership in event_group.ownerships}
    #
    # if current_user_id not in owners_and_moderators:
    #     raise OperationIsNotAllowed()

    try:
        from src.api.parse.utils import validate_calendar

        calendar = icalendar.Calendar.from_ical(await ics_file.read())
        validate_calendar(calendar)
    except ValueError as e:
        return JSONResponse(status_code=400, content={"detail": f"File is not valid:\n{e}"})

    content = calendar.to_ical()

    ics_path = locate_ics_by_path(event_group_path)

    if ics_path.exists():
        async with aiofiles.open(ics_path, "rb") as f:
            old_content = await f.read()
            if old_content == content:
                return JSONResponse(status_code=200, content={"detail": "File already exists and content is the same"})
    # make directory if not exists
    ics_path.parent.mkdir(parents=True, exist_ok=True)
    async with aiofiles.open(ics_path, "wb") as f:
        await f.write(content)

    await event_group_repository.update_timestamp(event_group_id)

    return JSONResponse(status_code=201, content={"detail": "File uploaded successfully"})


# ^^^^^^^^^^^^^ ICS-related ^^^^^^^^^^^^^^^^^^^^^^^^ #
