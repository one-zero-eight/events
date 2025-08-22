import asyncio
import datetime
import html
import logging
from collections.abc import AsyncGenerator
from pathlib import Path
from urllib.parse import quote
from zlib import crc32

import aiofiles
import httpx
import icalendar
from fastapi import HTTPException
from pydantic import BaseModel, TypeAdapter

from src.config import settings
from src.modules.event_groups.repository import event_group_repository
from src.modules.innohassle_accounts import innohassle_accounts
from src.modules.parse.utils import aware_utcnow, get_base_calendar, locate_ics_by_path
from src.modules.predefined.repository import predefined_repository
from src.modules.users.schemas import ViewUser

TIMEOUT = 60
MAX_SIZE = 10 * 1024 * 1024
MOSCOW_TZ = datetime.timezone(datetime.timedelta(hours=3), name="Europe/Moscow")


async def generate_ics_from_url(url: str, headers: dict = None) -> AsyncGenerator[bytes, None]:
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, timeout=TIMEOUT, headers=headers)
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            # reraise as HTTPException
            raise HTTPException(status_code=e.response.status_code, detail=e.response.text) from e

        # read from stream
        size: int | None = int(response.headers.get("Content-Length"))

        if size is None or size > MAX_SIZE:
            raise HTTPException(status_code=400, detail="File is too big or Content-Length is not specified")

        async for chunk in response.aiter_bytes():
            size -= len(chunk)
            if size < 0:
                raise HTTPException(status_code=400, detail="File is too big")
            yield chunk


async def _generate_ics_from_multiple(user: ViewUser, *ics: Path) -> AsyncGenerator[bytes, None]:
    async def _async_read_schedule(ics_path: Path):
        async with aiofiles.open(ics_path) as f:
            content = await f.read()
            _cal = icalendar.Calendar.from_ical(content)
            return _cal

    tasks = [_async_read_schedule(ics_path) for ics_path in ics]
    calendars = await asyncio.gather(*tasks)
    main_calendar = get_base_calendar()
    main_calendar["x-wr-calname"] = f"{user.email} schedule from innohassle.ru"
    ical_bytes = main_calendar.to_ical()
    # remove END:VCALENDAR
    ical_bytes = ical_bytes.removesuffix(b"END:VCALENDAR\r\n")
    yield ical_bytes

    for calendar in calendars:
        calendar: icalendar.Calendar
        vevents = calendar.walk(name="VEVENT")
        for vevent in vevents:
            vevent: icalendar.Event
            vevent["x-wr-origin"] = calendar["x-wr-calname"]
            yield vevent.to_ical()
    yield b"END:VCALENDAR"


async def get_personal_event_groups_ics(user: ViewUser) -> AsyncGenerator[bytes, None]:
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


async def get_personal_music_room_ics(user: ViewUser) -> AsyncGenerator[bytes, None]:
    if settings.music_room is None:
        raise HTTPException(status_code=404, detail="Music room is not configured")
    # check if user registered in music room
    async with httpx.AsyncClient() as client:
        url = f"{settings.music_room.api_url}/users/user_id"
        query_params = {"email": user.email}
        headers = {"Authorization": f"Bearer {settings.music_room.api_key.get_secret_value()}"}
        response = await client.get(url, params=query_params, headers=headers)
        response.raise_for_status()
        if response.status_code == 200:
            user_id = response.json()
            if user_id is None:
                raise HTTPException(status_code=404, detail="User not found in music room service")
        else:
            raise HTTPException(status_code=500, detail="Error in music room service")
    ical_generator = generate_ics_from_url(
        f"{settings.music_room.api_url}/users/{user_id}/bookings.ics",
        headers={"Authorization": f"Bearer {settings.music_room.api_key.get_secret_value()}"},
    )
    return ical_generator


async def get_personal_workshops_ics(user: ViewUser) -> bytes:
    """
    GET */users/{innohassle_user_id}/checkins

    [
        {
            "id": "b1d378a5-fe1b-47c6-b920-12acf77fcf1a",
            "dtstart": "2025-08-15T18:40:30.289000Z",
            "dtend": "2025-08-15T18:59:30.289000Z",
            "name": "W3",
            "description": null,
            "place": null,
        },
        ...
    ]
    """

    def _workshop_to_vevent(workshop: dict) -> icalendar.Event:
        string_to_hash = str(workshop["id"])
        hash_ = crc32(string_to_hash.encode("utf-8"))
        uid = f"workshop-{abs(hash_):x}@innohassle.ru"

        vevent = icalendar.Event()
        vevent.add("uid", uid)

        vevent.add("summary", workshop["name"])
        if workshop.get("place") is not None:
            vevent.add("location", workshop["place"])
        if workshop.get("description") is not None:
            vevent.add("description", workshop["description"])
        _dtstart = datetime.datetime.fromisoformat(workshop["dtstart"])
        _dtstart = _dtstart.astimezone(MOSCOW_TZ)
        _dtend = datetime.datetime.fromisoformat(workshop["dtend"])
        _dtend = _dtend.astimezone(MOSCOW_TZ)
        vevent.add("dtstart", icalendar.vDatetime(_dtstart))
        vevent.add("dtend", icalendar.vDatetime(_dtend))
        vevent.add("x-workshop-id", workshop["id"])
        return vevent

    main_calendar = get_base_calendar()
    main_calendar["x-wr-calname"] = f"{user.email} Workshops schedule from innohassle.ru"

    async with httpx.AsyncClient(
        headers={"Authorization": f"Bearer {settings.workshops.api_key.get_secret_value()}"}, timeout=TIMEOUT
    ) as client:
        response = await client.get(f"{settings.workshops.api_url}/users/{user.innohassle_id}/checkins")
        if response.status_code == 404 and "User not found" in response.text:
            raise HTTPException(status_code=404, detail="User not found in workshops service")
        response.raise_for_status()
        workshops = response.json()

    for workshop in workshops:
        event = _workshop_to_vevent(workshop)
        main_calendar.add_component(event)

    ical_bytes = main_calendar.to_ical()
    return ical_bytes


class Training(BaseModel):
    class ExtendedProps(BaseModel):
        id: int
        group_id: int
        can_grade: bool
        training_class: str | None
        group_accredited: bool
        can_check_in: bool
        checked_in: bool

    title: str
    start: datetime.datetime
    end: datetime.datetime
    allDay: bool = False
    extendedProps: ExtendedProps


async def get_personal_sport_ics(user: ViewUser) -> bytes:
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

    def _training_to_vevent(training: Training) -> icalendar.Event:
        string_to_hash = str(training.extendedProps.id)
        hash_ = crc32(string_to_hash.encode("utf-8"))
        uid = f"sport-{abs(hash_):x}@innohassle.ru"

        vevent = icalendar.Event()
        vevent.add("uid", uid)

        vevent.add("summary", training.title)
        if training.allDay:
            vevent.add("dtstart", icalendar.vDate(training.start.date()))
            vevent.add("dtend", icalendar.vDate(training.end.date()))
        else:
            vevent.add("dtstart", icalendar.vDatetime(training.start))
            vevent.add("dtend", icalendar.vDatetime(training.end))
        if training.extendedProps.training_class is not None:
            vevent.add("location", training.extendedProps.training_class)
        vevent.add("x-sport-training-id", training.extendedProps.id)
        vevent.add("x-sport-checked-in", training.extendedProps.checked_in)
        vevent.add("x-sport-can-checkin", training.extendedProps.can_check_in)
        return vevent

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


async def get_moodle_ics(user: ViewUser) -> bytes:
    """
    Get schedule in ICS format for the user from user link to moodle calendar;
    """

    def get_course_name(event: icalendar.Event) -> str:
        categories = (event["categories"]).to_ical().decode(encoding="utf-8")
        course_name = html.unescape(categories.split("]")[1].replace(r"\;", ";"))
        return course_name

    def make_deadline(event: icalendar.Event) -> icalendar.Event:
        new = icalendar.Event()
        end: datetime.datetime = event["dtend"].dt
        end = end.astimezone(MOSCOW_TZ)
        new["dtstart"] = icalendar.vDate(end.date())
        new["uid"] = event["uid"]
        new["dtstamp"] = event["dtstamp"]
        course_name = get_course_name(event)
        new["summary"] = event["summary"] + f" - {course_name}"

        new["description"] = f"Course: {course_name}\nDue to: {end.timetz().isoformat()}"

        return new

    def create_quiz(quiz_name: str, opens: icalendar.Event, closes: icalendar.Event | None = None) -> icalendar.Event:
        new = icalendar.Event()
        start: datetime.datetime = opens["dtstart"].dt
        start = start.astimezone(MOSCOW_TZ)
        due: datetime.datetime | None = None
        if closes:
            due = closes["dtend"].dt
            due = due.astimezone(MOSCOW_TZ)
        if due and start.date() != due.date():  # Display only on deadline day
            new["dtstart"] = icalendar.vDate(due.date())
        else:
            new["dtstart"] = icalendar.vDatetime(start)
            if due:
                new["dtend"] = icalendar.vDatetime(due)

        new["uid"] = opens["uid"]
        new["dtstamp"] = opens["dtstamp"]
        course_name = get_course_name(opens)
        new["summary"] = quiz_name + f" - {course_name}"

        new["description"] = "\n".join(
            filter(
                bool,
                [
                    f"Course: {course_name}",
                    opens["description"],
                    f"Due to: {due.timetz().isoformat()}" if due else None,
                ],
            )
        )

        new["color"] = "darkorange"
        return new

    async def read_moodle_schedule(url: str) -> icalendar.Calendar:
        _generator = generate_ics_from_url(url)
        content = "".join([bytes_data.decode("utf-8") async for bytes_data in _generator if bytes_data is not None])
        calendar = icalendar.Calendar.from_ical(content)
        return calendar

    async def _async_fix_moodle_events(calendar: icalendar.Calendar) -> icalendar.Calendar:
        fixed_calendar = get_base_calendar()
        fixed_calendar["x-wr-calname"] = "Moodle"

        vevents = calendar.walk(name="VEVENT")
        fixed_events = []
        quizes_halfs_opens = {}
        quizes_halfs_closes = {}

        for event in vevents:
            event: icalendar.Event
            event_timedelta = event["dtend"].dt - event["dtstart"].dt
            event_name: str = event["summary"].strip()

            if event_timedelta == datetime.timedelta():
                if event_name.endswith("opens"):
                    quiz_name = event_name.split("opens")[0].strip()
                    if quiz_name in quizes_halfs_opens:
                        logging.warning(f"Quiz '{quiz_name}' appears twice")
                    quizes_halfs_opens[quiz_name] = event
                elif event_name.endswith("открывается"):
                    quiz_name = event_name.split("открывается")[0].strip()
                    if quiz_name in quizes_halfs_opens:
                        logging.warning(f"Quiz '{quiz_name}' appears twice")
                    quizes_halfs_opens[quiz_name] = event
                elif event_name.endswith("closes"):
                    quiz_name = event_name.split("closes")[0].strip()
                    if quiz_name in quizes_halfs_closes:
                        logging.warning(f"Quiz '{quiz_name}' appears twice")
                    quizes_halfs_closes[quiz_name] = event
                elif event_name.endswith("закрывается"):
                    quiz_name = event_name.split("закрывается")[0].strip()
                    if quiz_name in quizes_halfs_closes:
                        logging.warning(f"Quiz '{quiz_name}' appears twice")
                    quizes_halfs_closes[quiz_name] = event
                else:
                    # DEADLINE TYPE
                    deadline = make_deadline(event)
                    fixed_events.append(deadline)
            else:
                if "Attendance" in event_name:
                    continue

                categories = (event["categories"]).to_ical().decode(encoding="utf-8")
                if categories:
                    if "]" in categories:
                        course_name = categories.split("]")[1]
                    else:
                        course_name = categories
                    event["summary"] = event["summary"] + f" - {course_name}"
                    event["description"] = "\n".join(
                        [
                            f"Course: {course_name}",
                            event["description"],
                        ]
                    )

                start = event["dtstart"]
                if start:
                    start = start.dt.astimezone(MOSCOW_TZ)
                    event["dtstart"] = icalendar.vDatetime(start)

                end = event["dtend"]
                if end:
                    end = end.dt.astimezone(MOSCOW_TZ)
                    event["dtend"] = icalendar.vDatetime(end)

                fixed_events.append(event)

        for quiz_name, opens in quizes_halfs_opens.items():
            closes = quizes_halfs_closes.get(quiz_name)

            if closes:  # Paired
                quiz = create_quiz(quiz_name, opens, closes)
                fixed_events.append(quiz)
            else:  # Non pair (no deadline)
                quiz = create_quiz(quiz_name, opens, closes=None)
                fixed_events.append(quiz)

        for event in fixed_events:
            event["color"] = "darkorange"
            fixed_calendar.add_component(event)

        return fixed_calendar

    token = user.moodle_calendar_authtoken
    assert token is not None
    encoded_token = quote(token)
    user_moodle_calendar_url = (
        f"https://moodle.innopolis.university/calendar/export_execute.php?"
        f"userid={user.moodle_userid}&authtoken={encoded_token}&preset_what=all&preset_time=custom"
    )
    moodle_calendar = await read_moodle_schedule(user_moodle_calendar_url)
    calendar = await _async_fix_moodle_events(moodle_calendar)
    return calendar.to_ical()
