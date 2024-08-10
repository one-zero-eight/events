import asyncio
import datetime
from pathlib import Path
from typing import AsyncGenerator, Optional
from zlib import crc32

import aiofiles
import httpx
import icalendar
from fastapi import HTTPException
from pydantic import BaseModel, TypeAdapter

from src.config import settings
from src.modules.event_groups.repository import event_group_repository
from src.modules.innohassle_accounts import innohassle_accounts
from src.modules.parse.utils import aware_utcnow, locate_ics_by_path, get_base_calendar
from src.modules.predefined.repository import predefined_repository
from src.modules.users.schemas import ViewUser

TIMEOUT = 60
MAX_SIZE = 10 * 1024 * 1024


async def _generate_ics_from_url(url: str, headers: dict = None) -> AsyncGenerator[bytes, None]:
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, timeout=TIMEOUT, headers=headers)
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            # reraise as HTTPException
            raise HTTPException(status_code=e.response.status_code, detail=e.response.text) from e

        # read from stream
        size: Optional[int] = int(response.headers.get("Content-Length"))

        if size is None or size > MAX_SIZE:
            raise HTTPException(status_code=400, detail="File is too big or Content-Length is not specified")

        async for chunk in response.aiter_bytes():
            size -= len(chunk)
            if size < 0:
                raise HTTPException(status_code=400, detail="File is too big")
            yield chunk


async def _generate_ics_from_multiple(user: ViewUser, *ics: Path) -> AsyncGenerator[bytes, None]:
    async def _async_read_schedule(ics_path: Path):
        async with aiofiles.open(ics_path, "r") as f:
            content = await f.read()
            _cal = icalendar.Calendar.from_ical(content)
            return _cal

    tasks = [_async_read_schedule(ics_path) for ics_path in ics]
    calendars = await asyncio.gather(*tasks)
    main_calendar = get_base_calendar()
    main_calendar["x-wr-calname"] = f"{user.email} schedule from innohassle.ru"
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


async def _get_personal_ics(user: ViewUser) -> AsyncGenerator[bytes, None]:
    hidden = set(user.hidden_event_groups)
    predefined = await predefined_repository.get_user_predefined(user.id)
    all_user_event_groups = set(user.favorite_event_groups) | set(predefined)

    nonhidden = all_user_event_groups - hidden
    paths = set()
    for event_group_id in nonhidden:
        event_group = await event_group_repository.read(event_group_id)
        if event_group.path is None:
            raise HTTPException(
                status_code=501,
                detail="Can not create .ics file for event group on the fly (set static .ics file for the event group",
            )
        ics_path = locate_ics_by_path(event_group.path)
        paths.add(ics_path)
    ical_generator = _generate_ics_from_multiple(user, *paths)
    return ical_generator


async def _get_personal_music_room_ics(user: ViewUser) -> AsyncGenerator[bytes, None]:
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


class Training(BaseModel):
    class ExtendedProps(BaseModel):
        id: int
        group_id: int
        can_grade: bool
        training_class: str
        group_accredited: bool
        can_check_in: bool
        checked_in: bool

    title: str
    start: datetime.datetime
    end: datetime.datetime
    allDay: bool = False
    extendedProps: ExtendedProps


async def _get_personal_sport_ics(user: ViewUser) -> bytes:
    """
    GET /calendar/trainings

    [
      {
        "title": "Football",
        "start": "2024-03-09T17:00:00+03:00",
        "end": "2024-03-09T19:00:00+03:00",
        "allDay": false,
        "extendedProps": {
          "id": 32133,
          "can_edit": true,
          "group_id": 560,
          "can_grade": false,
          "training_class": "[SC] Big Hall",
          "group_accredited": true,
          "can_check_in": false,
          "checked_in": false
        }
      },
      {
        "title": "Table tennis - Beginners",
        "start": "2024-03-10T10:00:00+03:00",
        "end": "2024-03-10T11:30:00+03:00",
        "allDay": false,
        "extendedProps": {
          "id": 31640,
          "can_edit": true,
          "group_id": 551,
          "can_grade": false,
          "training_class": "[SC] 2nd floor",
          "group_accredited": true,
          "can_check_in": false,
          "checked_in": false
        }
      }
    ]
    """

    main_calendar = get_base_calendar()
    main_calendar["x-wr-calname"] = f"{user.email} Sport schedule from innohassle.ru"

    sport_token = await innohassle_accounts.get_sport_token(user.innohassle_id)
    _now = aware_utcnow()
    _start = _now - datetime.timedelta(days=7)
    _end = _now + datetime.timedelta(days=7)

    async with httpx.AsyncClient(headers={"Authorization": f"Bearer {sport_token}"}, timeout=TIMEOUT) as client:
        response = await client.get(
            f"{settings.sport.api_url}/calendar/trainings",
            params={"start": _start.isoformat(), "end": _end.isoformat()},
        )
        response.raise_for_status()
        type_adapter = TypeAdapter(list[Training])
        trainings = type_adapter.validate_python(response.json())

    for training in trainings:
        if not training.extendedProps.checked_in:
            continue
        event = _training_to_vevent(training)
        main_calendar.add_component(event)

    ical_bytes = main_calendar.to_ical()
    return ical_bytes


def _training_to_vevent(training: Training) -> icalendar.Event:
    string_to_hash = str(training.extendedProps.id)
    hash_ = crc32(string_to_hash.encode("utf-8"))
    uid = "sport-%x@innohassle.ru" % abs(hash_)

    vevent = icalendar.Event()
    vevent.add("uid", uid)

    vevent.add("summary", training.title)
    if training.allDay:
        vevent.add("dtstart", icalendar.vDate(training.start.date()))
        vevent.add("dtend", icalendar.vDate(training.end.date()))
    else:
        vevent.add("dtstart", icalendar.vDatetime(training.start))
        vevent.add("dtend", icalendar.vDatetime(training.end))
    vevent.add("location", training.extendedProps.training_class)
    vevent.add("x-sport-training-id", training.extendedProps.id)
    vevent.add("x-sport-checked-in", training.extendedProps.checked_in)
    vevent.add("x-sport-can-checkin", training.extendedProps.can_check_in)
    return vevent
