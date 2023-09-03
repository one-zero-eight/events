__all__ = ["PredefinedRepository", "JsonUserStorage", "JsonGroupStorage", "JsonTagStorage", "validate_calendar"]

import os.path
import warnings
from pathlib import Path
from typing import Optional

import dateutil.rrule
import icalendar
from pydantic import BaseModel, Field, parse_obj_as
from pydantic import validator

from src.config import settings


class JsonUserStorage(BaseModel):
    class InJsonUser(BaseModel):
        email: str
        groups: list[str] = Field(default_factory=list)

    users: list[InJsonUser] = Field(default_factory=list)

    @validator("users", pre=True, each_item=True, always=True)
    def _validate_user(cls, v):
        if isinstance(v, dict):
            return JsonUserStorage.InJsonUser(**v)
        return v

    @validator("users")
    def _should_be_unique(cls, v):
        emails = set()
        for user in v:
            if user.email in emails:
                raise ValueError(f"User email {user.email} is not unique")
            emails.add(user.email)
        return v


class JsonGroupStorage(BaseModel):
    class PredefinedGroup(BaseModel):
        class TagReference(BaseModel):
            alias: str
            type: str

        alias: str
        name: Optional[str]
        path: Optional[str]
        description: Optional[str]
        tags: list[TagReference] = Field(default_factory=list)

    event_groups: list[PredefinedGroup] = Field(default_factory=list)

    @validator("event_groups", pre=True, each_item=True, always=True)
    def _validate_group(cls, v):
        if isinstance(v, dict):
            return JsonGroupStorage.PredefinedGroup(**v)
        return v

    @validator("event_groups")
    def _should_be_unique(cls, v):
        aliases = set()
        for group in v:
            if group.alias in aliases:
                raise ValueError(f"Group alias {group.alias} is not unique")
            aliases.add(group.alias)
        return v

    @validator("event_groups")
    def _path_should_be_unique_and_exist_and_valid(cls, v):
        paths = set()
        for group in v:
            if group.path in paths:
                raise ValueError(f"Group path {group.path} is not unique")
            paths.add(group.path)
            located = PredefinedRepository.locate_ics_by_path(group.path)
            if not os.path.exists(located):
                raise FileNotFoundError(f"ICS file for group {group.alias} not found")
            with open(located, "rb") as f:
                calendar = icalendar.Calendar.from_ical(f.read())
                try:
                    validate_calendar(calendar)
                except ValueError as e:
                    warnings.warn(f"ICS file for group {group.alias} is invalid:\n{e}")
        return v


class JsonTagStorage(BaseModel):
    class Tag(BaseModel):
        alias: str
        name: str
        type: str

    tags: list[Tag] = Field(default_factory=list)

    @validator("tags", pre=True, each_item=True, always=True)
    def _validate_tag(cls, v):
        if isinstance(v, dict):
            return JsonTagStorage.Tag(**v)
        return v

    @validator("tags")
    def _should_be_unique(cls, v):
        aliases = set()
        for tag in v:
            if tag.alias in aliases:
                raise ValueError(f"Tag alias {tag.alias} is not unique")
            aliases.add(tag.alias)
        return v


class PredefinedRepository:
    user_storage: JsonUserStorage
    event_group_storage: JsonGroupStorage
    tag_storage: JsonTagStorage

    def __init__(
        self, user_storage: JsonUserStorage, event_group_storage: JsonGroupStorage, tag_storage: JsonTagStorage
    ):
        self.user_storage = user_storage
        self.event_group_storage = event_group_storage
        self.tag_storage = tag_storage

        self.validate()

    @classmethod
    def from_jsons(cls, user_json: dict, event_group_json: dict, tag_json: dict):
        user_storage = parse_obj_as(JsonUserStorage, user_json)
        event_group_storage = parse_obj_as(JsonGroupStorage, event_group_json)
        tag_storage = parse_obj_as(JsonTagStorage, tag_json)
        return cls(user_storage, event_group_storage, tag_storage)

    def get_users(self) -> list[JsonUserStorage.InJsonUser]:
        return self.user_storage.users.copy()

    def get_event_groups(self) -> list[JsonGroupStorage.PredefinedGroup]:
        return self.event_group_storage.event_groups.copy()

    def get_tags(self) -> list[JsonTagStorage.Tag]:
        return self.tag_storage.tags.copy()

    @staticmethod
    def locate_ics_by_path(path: str) -> Path:
        return settings.PREDEFINED_DIR / "ics" / path

    def validate(self):
        # validate mapping event_group <-> tag
        tag_aliases = set(tag.alias for tag in self.tag_storage.tags)
        for group in self.event_group_storage.event_groups:
            for tag in group.tags:
                if tag.alias not in tag_aliases:
                    raise ValueError(f"Tag {tag.alias} is not found")

        # validate mapping user <-> event_group
        group_aliases = set(group.alias for group in self.event_group_storage.event_groups)
        for user in self.user_storage.users:
            for group in user.groups:
                if group not in group_aliases:
                    raise ValueError(f"Group {group} is not found")


def validate_calendar(calendar: icalendar.Calendar):
    unique_ids = set()
    for event in calendar.walk("VEVENT"):
        event: icalendar.Event
        validate_vevent(event)

        uid = event["UID"]
        if uid in unique_ids:
            raise ValueError(f"Event UID ({uid}) is not unique", event)

        unique_ids.add(uid)


def validate_vevent(event: icalendar.Event):
    if "UID" not in event:
        raise ValueError("Event has no UID", event)
    #
    # if "DTSTAMP" not in event:
    #     raise ValueError("Event has no DTSTAMP", event)

    vddd_dtstart: icalendar.vDDDTypes | None = event.get("DTSTART")
    vddd_dtend: icalendar.vDDDTypes | None = event.get("DTEND")
    vddd_duration: icalendar.vDDDTypes | None = event.get("DURATION")

    if not vddd_dtstart:
        raise ValueError("Event has no DTSTART", event)

    if not vddd_dtend and not vddd_duration:
        raise ValueError("Event has no DTEND or DURATION", event)

    if vddd_dtend and vddd_duration:
        raise ValueError("Event has both DTEND and DURATION", event)

    if vddd_dtend and vddd_dtstart.dt > vddd_dtend.dt:
        raise ValueError("DTSTART is later than DTEND", event)

    if "RRULE" in event:
        # should be compatible with dtstart
        rrule: dateutil.rrule.rrule = dateutil.rrule.rrulestr(
            event["RRULE"].to_ical().decode(), dtstart=vddd_dtstart.dt
        )
        rrule_dates = rrule.__iter__()
        rrule_first_dt = next(rrule_dates)
        if rrule_first_dt != vddd_dtstart.dt:
            raise ValueError("RRULE is not compatible with DTSTART", event)
