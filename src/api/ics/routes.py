import asyncio
from pathlib import Path
from typing import AsyncGenerator, Optional

import aiofiles
import httpx
import icalendar
from fastapi import HTTPException
from starlette.responses import FileResponse, StreamingResponse

from src.api.dependencies import Shared, CURRENT_USER_ID_DEPENDENCY
from src.api.ics import router
from src.config import settings
from src.exceptions import EventGroupNotFoundException, UserNotFoundException, ForbiddenException
from src.repositories.event_groups import SqlEventGroupRepository
from src.repositories.predefined import PredefinedRepository
from src.repositories.users import SqlUserRepository
from src.schemas import ViewUser
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
    user_repository = Shared.f(SqlUserRepository)
    user = await user_repository.read(user_id)

    ical_generator = await get_personal_ics(user)

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
        **UserNotFoundException.responses,
        **ForbiddenException.responses,
    },
    tags=["Users"],
)
async def get_user_schedule(user_id: int, access_key: str) -> StreamingResponse:
    """
    Get schedule in ICS format for the user; requires access key for `/users/{user_id}/all.ics` resource
    """
    user_repository = Shared.f(SqlUserRepository)
    user = await user_repository.read(user_id)

    if user is None:
        raise UserNotFoundException()

    resource_path = f"/users/{user_id}/all.ics"
    if not await user_repository.check_user_schedule_key(user_id, access_key, resource_path):
        raise ForbiddenException()

    ical_generator = await get_personal_ics(user)

    return StreamingResponse(
        content=ical_generator,
        media_type="text/calendar",
    )


async def get_personal_ics(user: ViewUser) -> AsyncGenerator[bytes, None]:
    nonhidden = []
    for association in user.favorites_association:
        if not association.hidden:
            nonhidden.append(association)
    paths = set()
    for association in nonhidden:
        event_group = association.event_group
        if event_group.path is None:
            raise HTTPException(
                status_code=501,
                detail="Can not create .ics file for event group on the fly (set static .ics file for the event group",
            )
        ics_path = PredefinedRepository.locate_ics_by_path(event_group.path)
        paths.add(ics_path)
    ical_generator = _generate_ics_from_multiple(user, *paths)
    return ical_generator


@router.get(
    "/users/{user_id}/linked/{linked_alias}.ics",
    responses={
        200: {
            "description": "ICS file with schedule based on linked url",
            "content": {"text/calendar": {"schema": {"type": "string", "format": "binary"}}},
        },
        **UserNotFoundException.responses,
    },
    tags=["Users"],
)
async def get_user_linked_schedule(
    user_id: int,
    linked_alias: str,
) -> StreamingResponse:
    """
    Get schedule in ICS format for the user
    """
    user_repository = Shared.f(SqlUserRepository)
    user = await user_repository.read(user_id)

    if user is None:
        raise UserNotFoundException()

    if linked_alias not in user.linked_calendars:
        # TODO: Extract to exception
        raise HTTPException(status_code=404, detail="Linked calendar not found")

    linked_calendar: LinkedCalendarView = user.linked_calendars[linked_alias]

    ical_generator = _generate_ics_from_url(linked_calendar.url)

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
    user_repository = Shared.f(SqlUserRepository)
    user = await user_repository.read(user_id)
    if user is None:
        raise UserNotFoundException()

    ical_generator = await get_personal_music_room_ics(user)

    return StreamingResponse(
        content=ical_generator,
        media_type="text/calendar",
    )


@router.get(
    "/users/{user_id}/music-room.ics",
    responses={
        200: {
            "description": "ICS file with schedule of the music room booking",
            "content": {"text/calendar": {"schema": {"type": "string", "format": "binary"}}},
        },
        **UserNotFoundException.responses,
        **ForbiddenException.responses,
    },
    tags=["Users"],
)
async def get_music_room_user_schedule(user_id: int, access_key: str) -> StreamingResponse:
    """
    Get schedule in ICS format for the user; requires access key for `/users/{user_id}/music-room.ics` resource
    """
    user_repository = Shared.f(SqlUserRepository)
    user = await user_repository.read(user_id)
    if user is None:
        raise UserNotFoundException()

    resource_path = f"/users/{user_id}/music-room.ics"
    if not await user_repository.check_user_schedule_key(user_id, access_key, resource_path):
        raise ForbiddenException()

    ical_generator = await get_personal_music_room_ics(user)

    return StreamingResponse(content=ical_generator, media_type="text/calendar")


async def get_personal_music_room_ics(user: ViewUser) -> AsyncGenerator[bytes, None]:
    if settings.music_room is None:
        raise HTTPException(status_code=404, detail="Music room is not configured")
    # check if user registered in music room
    async with httpx.AsyncClient() as client:
        url = f"{settings.music_room.api_url}/participants/participant_id"
        query_params = {"email": user.email}
        headers = {"Authorization": f"Bearer {settings.music_room.api_key.get_secret_value()}"}
        response = await client.get(url, params=query_params, headers=headers)
        response.raise_for_status()
        if response.status_code == 200:
            participant_id = response.json()
            if participant_id is None:
                raise HTTPException(status_code=404, detail="User not found in music room service")
        else:
            raise HTTPException(status_code=500, detail="Error in music room service")
    ical_generator = _generate_ics_from_url(
        f"{settings.music_room.api_url}/participants/{participant_id}/bookings.ics",
        headers={"Authorization": f"Bearer {settings.music_room.api_key.get_secret_value()}"},
    )
    return ical_generator


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


async def _generate_ics_from_multiple(user: ViewUser, *ics: Path) -> AsyncGenerator[bytes, None]:
    async def _async_read_schedule(ics_path: Path):
        async with aiofiles.open(ics_path, "r") as f:
            content = await f.read()
            calendar = icalendar.Calendar.from_ical(content)
            return calendar

    tasks = [_async_read_schedule(ics_path) for ics_path in ics]
    calendars = await asyncio.gather(*tasks)
    main_calendar = icalendar.Calendar(
        prodid="-//one-zero-eight//InNoHassle Schedule",
        version="2.0",
        method="PUBLISH",
    )
    main_calendar["x-wr-calname"] = f"{user.email} schedule from innohassle.ru"
    main_calendar["x-wr-timezone"] = "Europe/Moscow"
    main_calendar["x-wr-caldesc"] = "Generated by InNoHassle Schedule"
    ical_bytes = main_calendar.to_ical()
    # remove END:VCALENDAR
    ical_bytes = ical_bytes[:-13]
    yield ical_bytes

    for calendar in calendars:
        calendar: icalendar.Calendar
        vevents = calendar.walk(name="VEVENT")
        for vevent in vevents:
            vevent: icalendar.Event
            vevent["x-wr-origin"] = calendar["x-wr-calname"]
            yield vevent.to_ical()
    yield b"END:VCALENDAR"


async def _generate_ics_from_url(url: str, headers: dict = None) -> AsyncGenerator[bytes, None]:
    async with httpx.AsyncClient() as client:
        # TODO: add config for timeout
        try:
            response = await client.get(url, timeout=10, headers=headers)
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            # reraise as HTTPException
            raise HTTPException(status_code=e.response.status_code, detail=e.response.text) from e

        # read from stream
        size: Optional[int] = int(response.headers.get("Content-Length"))
        # TODO: add config for max size
        if size is None or size > 10 * 1024 * 1024:
            # TODO: Extract to exception
            raise HTTPException(status_code=400, detail="File is too big or Content-Length is not specified")

        async for chunk in response.aiter_bytes():
            size -= len(chunk)
            if size < 0:
                raise HTTPException(status_code=400, detail="File is too big")
            yield chunk


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
    event_group_repository = Shared.f(SqlEventGroupRepository)
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
