from urllib.parse import unquote

from fastapi import APIRouter
from fastapi import HTTPException
from starlette.responses import FileResponse, StreamingResponse, Response

from src.api.dependencies import CURRENT_USER_ID_DEPENDENCY
from src.config import settings
from src.exceptions import EventGroupNotFoundException, ObjectNotFound, ForbiddenException
from src.modules.event_groups.repository import event_group_repository
from src.modules.ics.utils import (
    generate_ics_from_url,
    get_personal_event_groups_ics,
    get_personal_sport_ics,
    get_personal_music_room_ics,
    get_moodle_ics,
)
from src.modules.parse.utils import locate_ics_by_path
from src.modules.users.linked import LinkedCalendarView
from src.modules.users.repository import user_repository

router = APIRouter(prefix="", tags=["ICS"])


@router.get(
    "/users/me/all.ics",
    responses={
        200: {
            "description": "ICS file with schedule based on favorites (non-hidden)",
            "content": {"text/calendar": {"schema": {"type": "string", "format": "binary"}}},
        },
    },
    tags=["Users"],
)
async def get_current_user_schedule(user_id: CURRENT_USER_ID_DEPENDENCY) -> StreamingResponse:
    """
    Get schedule in ICS format for the current user
    """

    user = await user_repository.read(user_id)

    ical_generator = await get_personal_event_groups_ics(user)

    return StreamingResponse(
        content=ical_generator,
        media_type="text/calendar",
    )


@router.get(
    "/users/{user_id}/all.ics",
    responses={
        200: {
            "description": "ICS file with schedule based on favorites (non-hidden)",
            "content": {"text/calendar": {"schema": {"type": "string", "format": "binary"}}},
        },
        **ObjectNotFound.responses,
        **ForbiddenException.responses,
    },
    tags=["Users"],
)
async def get_user_schedule(user_id: int, access_key: str) -> StreamingResponse:
    """
    Get schedule in ICS format for the user; requires access key for `/users/{user_id}/all.ics` resource
    """

    user = await user_repository.read(user_id)

    if user is None:
        raise ObjectNotFound()

    resource_path = f"/users/{user_id}/all.ics"
    if not await user_repository.check_user_schedule_key(user_id, access_key, resource_path):
        raise ForbiddenException()

    ical_generator = await get_personal_event_groups_ics(user)

    return StreamingResponse(
        content=ical_generator,
        media_type="text/calendar",
    )


@router.get(
    "/users/me/music-room.ics",
    responses={
        200: {
            "description": "ICS file with schedule of the music room booking",
            "content": {"text/calendar": {"schema": {"type": "string", "format": "binary"}}},
        },
    },
    tags=["Users"],
)
async def get_music_room_current_user_schedule(user_id: CURRENT_USER_ID_DEPENDENCY) -> StreamingResponse:
    """
    Get schedule in ICS format for the current user
    """

    user = await user_repository.read(user_id)
    if user is None:
        raise ObjectNotFound()

    ical_generator = await get_personal_music_room_ics(user)

    return StreamingResponse(content=ical_generator, media_type="text/calendar")


@router.get(
    "/users/{user_id}/music-room.ics",
    responses={
        200: {
            "description": "ICS file with schedule of the music room booking",
            "content": {"text/calendar": {"schema": {"type": "string", "format": "binary"}}},
        },
        **ObjectNotFound.responses,
        **ForbiddenException.responses,
    },
    tags=["Users"],
)
async def get_music_room_user_schedule(user_id: int, access_key: str) -> StreamingResponse:
    """
    Get schedule in ICS format for the user; requires access key for `/users/{user_id}/music-room.ics` resource
    """

    user = await user_repository.read(user_id)
    if user is None:
        raise ObjectNotFound()

    resource_path = f"/users/{user_id}/music-room.ics"
    if not await user_repository.check_user_schedule_key(user_id, access_key, resource_path):
        raise ForbiddenException()

    ical_generator = await get_personal_music_room_ics(user)

    return StreamingResponse(content=ical_generator, media_type="text/calendar")


@router.get(
    "/users/me/sport.ics",
    responses={
        200: {
            "description": "ICS file with your sport check-ins",
            "content": {"text/calendar": {"schema": {"type": "string", "format": "binary"}}},
        },
    },
    tags=["Users"],
)
async def get_sport_current_user_schedule(user_id: CURRENT_USER_ID_DEPENDENCY) -> Response:
    """
    Get schedule in ICS format for the current user
    """

    user = await user_repository.read(user_id)
    if user is None:
        raise ObjectNotFound()

    ical_bytes = await get_personal_sport_ics(user)
    return Response(content=ical_bytes, media_type="text/calendar")


@router.get(
    "/users/{user_id}/sport.ics",
    responses={
        200: {
            "description": "ICS file with your sport check-ins",
            "content": {"text/calendar": {"schema": {"type": "string", "format": "binary"}}},
        },
        **ObjectNotFound.responses,
        **ForbiddenException.responses,
    },
    tags=["Users"],
)
async def get_sport_user_schedule(user_id: int, access_key: str) -> Response:
    """
    Get schedule in ICS format for the user; requires access key for `/users/{user_id}/sport.ics` resource
    """

    user = await user_repository.read(user_id)
    if user is None:
        raise ObjectNotFound()

    resource_path = f"/users/{user_id}/sport.ics"
    if not await user_repository.check_user_schedule_key(user_id, access_key, resource_path):
        raise ForbiddenException()

    ical_bytes = await get_personal_sport_ics(user)
    return Response(content=ical_bytes, media_type="text/calendar")


@router.get(
    "/users/me/moodle.ics",
    responses={
        200: {
            "description": "ICS file with your schedule from moodle",
            "content": {"text/calendar": {"schema": {"type": "string", "format": "binary"}}},
        },
        **ObjectNotFound.responses,
        **ForbiddenException.responses,
    },
    tags=["Users"],
)
async def get_moodle_user_schedule(user_id: CURRENT_USER_ID_DEPENDENCY) -> Response:
    """
    Get schedule in ICS format for the current user
    """

    user = await user_repository.read(user_id)
    if user is None:
        raise ObjectNotFound()

    if user.moodle_userid is None or user.moodle_calendar_authtoken is None:
        raise HTTPException(status_code=404, detail="Moodle for user is not configured")

    ical_bytes = await get_moodle_ics(user)

    return Response(content=ical_bytes, media_type="text/calendar")


@router.get(
    "/users/{user_id}/moodle.ics",
    responses={
        200: {
            "description": "ICS file with your schedule from moodle",
            "content": {"text/calendar": {"schema": {"type": "string", "format": "binary"}}},
        },
        **ObjectNotFound.responses,
        **ForbiddenException.responses,
    },
    tags=["Users"],
)
async def get_moodle_current_user_schedule(user_id: int, access_key: str) -> Response:
    """
    Get schedule in ICS format for the user; requires access key for `/users/{user_id}/moodle.ics` resource
    """

    user = await user_repository.read(user_id)
    if user is None:
        raise ObjectNotFound()

    resource_path = f"/users/{user_id}/moodle.ics"
    if not await user_repository.check_user_schedule_key(user_id, access_key, resource_path):
        raise ForbiddenException()

    if user.moodle_userid is None or user.moodle_calendar_authtoken is None:
        raise HTTPException(status_code=404, detail="Moodle for user is not configured")

    ical_bytes = await get_moodle_ics(user)

    return Response(content=ical_bytes, media_type="text/calendar")


@router.get(
    "/users/{user_id}/linked/{linked_alias}.ics",
    responses={
        200: {
            "description": "ICS file with schedule based on linked url",
            "content": {"text/calendar": {"schema": {"type": "string", "format": "binary"}}},
        },
        **ObjectNotFound.responses,
    },
    tags=["Users"],
)
async def get_user_linked_schedule(user_id: int, linked_alias: str) -> StreamingResponse:
    """
    Get schedule in ICS format for the user
    """

    user = await user_repository.read(user_id)

    if user is None:
        raise ObjectNotFound(f"User with id {user_id} not found")

    if linked_alias not in user.linked_calendars:
        raise ObjectNotFound(f"Linked calendar with alias {linked_alias} not found")

    linked_calendar: LinkedCalendarView = user.linked_calendars[linked_alias]

    ical_generator = generate_ics_from_url(linked_calendar.url)

    return StreamingResponse(content=ical_generator, media_type="text/calendar")


@router.get(
    "/music-room.ics",
    responses={
        200: {
            "description": "ICS file with schedule of the music room",
            "content": {"text/calendar": {"schema": {"type": "string", "format": "binary"}}},
        },
    },
    response_class=StreamingResponse,
)
async def get_music_room_schedule() -> StreamingResponse:
    """
    Get schedule in ICS format for the music room
    """
    if settings.music_room is None:
        raise HTTPException(status_code=404, detail="Music room is not configured")

    ical_generator = generate_ics_from_url(f"{settings.music_room.api_url}/music-room.ics")

    return StreamingResponse(content=ical_generator, media_type="text/calendar")


@router.get(
    "/{event_group_alias}.ics",
    response_class=FileResponse,
    responses={
        200: {
            "description": "ICS file with schedule of the event-group",
            "content": {"text/calendar": {"schema": {"type": "string", "format": "binary"}}},
        },
        **EventGroupNotFoundException.responses,
    },
    tags=["Event Groups"],
)
async def get_event_group_ics_by_alias(user_id: int, export_type: str, event_group_alias: str):
    """
    Get event group .ics file by id
    """

    event_group_alias = unquote(event_group_alias)
    event_group = await event_group_repository.read_by_alias(event_group_alias)

    if event_group is None:
        raise EventGroupNotFoundException()
    if event_group.path:
        ics_path = locate_ics_by_path(event_group.path)
        return FileResponse(ics_path, media_type="text/calendar")
    else:
        # TODO: create ics file on the fly from events connected to event group
        raise HTTPException(
            status_code=501, detail="Can not create .ics file on the fly (set static .ics file for the event group"
        )
