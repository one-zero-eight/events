from fastapi import HTTPException
from starlette.responses import FileResponse, StreamingResponse, Response

from src.api.dependencies import CURRENT_USER_ID_DEPENDENCY
from src.api.ics import router
from src.api.ics.utils import (
    _get_personal_music_room_ics,
    _generate_ics_from_url,
    _get_personal_ics,
    _get_personal_sport_ics,
    locate_ics_by_path,
)
from src.config import settings
from src.exceptions import EventGroupNotFoundException, ObjectNotFound, ForbiddenException
from src.repositories.event_groups.repository import event_group_repository
from src.repositories.users.repository import user_repository
from src.schemas.linked import LinkedCalendarView


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

    ical_generator = await _get_personal_ics(user)

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

    ical_generator = await _get_personal_ics(user)

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

    ical_generator = await _get_personal_music_room_ics(user)

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

    ical_generator = await _get_personal_music_room_ics(user)

    return StreamingResponse(content=ical_generator, media_type="text/calendar")


@router.get(
    "/users/me/sport.ics",
    responses={
        200: {
            "description": "ICS file with schedule of the music room booking",
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

    ical_bytes = await _get_personal_sport_ics(user)
    return Response(content=ical_bytes, media_type="text/calendar")


@router.get(
    "/users/{user_id}/sport.ics",
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

    ical_bytes = await _get_personal_sport_ics(user)
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

    ical_generator = _generate_ics_from_url(linked_calendar.url)

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

    ical_generator = _generate_ics_from_url(f"{settings.music_room.api_url}/music-room.ics")

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
