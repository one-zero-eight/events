import asyncio
from pathlib import Path
from typing import AsyncGenerator, Optional

import aiofiles
import httpx
import icalendar
from fastapi import HTTPException
from starlette.responses import FileResponse, StreamingResponse

from src.api.dependencies import Shared
from src.api.ics import router
from src.exceptions import EventGroupNotFoundException, UserNotFoundException
from src.repositories.event_groups import SqlEventGroupRepository
from src.repositories.predefined import PredefinedRepository
from src.repositories.users import SqlUserRepository
from src.schemas import ViewUser
from src.schemas.linked import LinkedCalendarView


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


@router.get(
    "/users/{user_id}.ics",
    responses={
        200: {
            "description": "ICS file with schedule based on favorites (non-hidden)",
            "content": {"text/calendar": {"schema": {"type": "string", "format": "binary"}}},
        },
        **UserNotFoundException.responses,
    },
)
async def get_user_schedule(
    user_id: int,
) -> StreamingResponse:
    """
    Get schedule in ICS format for the user
    """
    user_repository = Shared.f(SqlUserRepository)
    user = await user_repository.read(user_id)

    if user is None:
        raise UserNotFoundException()

    user: ViewUser
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

    return StreamingResponse(
        content=ical_generator,
        media_type="text/calendar",
    )


# TODO: Extract to separated service with cache, task queue based on FastAPI, Celery + Redis
@router.get(
    "/users/{user_id}/linked/{linked_alias}.ics",
    responses={
        200: {
            "description": "ICS file with schedule based on linked url",
            "content": {"text/calendar": {"schema": {"type": "string", "format": "binary"}}},
        },
        **UserNotFoundException.responses,
    },
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


async def _generate_ics_from_url(url: str) -> AsyncGenerator[bytes, None]:
    async with httpx.AsyncClient() as client:
        # TODO: add config for timeout
        try:
            response = await client.get(url, timeout=10)
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
