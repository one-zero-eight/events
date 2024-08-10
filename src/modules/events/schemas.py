__all__ = ["CreateEvent", "ViewEvent", "UpdateEvent", "AddEventPatch", "ViewEventPatch", "UpdateEventPatch"]

import datetime
from typing import Optional

from icalendar import vRecur
from pydantic import BaseModel, Field, field_validator, ConfigDict


class CreateEvent(BaseModel):
    name: str
    description: Optional[str] = None
    patches: list["AddEventPatch"] = Field(default_factory=list)


class ViewEvent(BaseModel):
    id: int
    name: str
    description: Optional[str] = None

    patches: list["ViewEventPatch"] = Field(default_factory=list)
    model_config = ConfigDict(from_attributes=True)


class UpdateEvent(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


class AddEventPatch(BaseModel):
    type: str = "create"

    # --- .ics fields --- #
    summary: str
    description: Optional[str] = None
    location: Optional[str] = None

    dtstart: datetime.datetime
    dtend: datetime.datetime

    rrule: Optional[str | dict] = None

    @field_validator("rrule", mode="before")
    def _validate_rrule(cls, v) -> str:
        if isinstance(v, vRecur):
            v = v.to_ical().decode()
        elif isinstance(v, dict):
            v = vRecur(**v).to_ical().decode()
        elif isinstance(v, str):
            # validate ical string
            _ = vRecur(vRecur.from_ical(v))
            reverse = _.to_ical().decode()
            if v.upper() != reverse.upper():
                raise ValueError(f"Invalid ical string {v!r}")
        return v


class ViewEventPatch(BaseModel):
    id: int
    parent_id: int
    type: str

    # --- .ics fields --- #
    summary: str
    description: Optional[str] = None
    location: Optional[str] = None

    dtstart: datetime.datetime
    dtend: datetime.datetime

    rrule: Optional[vRecur] = None

    @field_validator("rrule", mode="before")
    def _validate_rrule(cls, v):
        if isinstance(v, str):
            return vRecur.from_ical(v)
        return v

    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)


class UpdateEventPatch(BaseModel):
    # --- .ics fields --- #
    summary: Optional[str] = None
    description: Optional[str] = None
    location: Optional[str] = None

    dtstart: Optional[datetime.datetime] = None
    dtend: Optional[datetime.datetime] = None

    rrule: Optional[vRecur] = None

    @field_validator("rrule", mode="before")
    def _validate_rrule(cls, v):
        if isinstance(v, str):
            return vRecur.from_ical(v)
        return v

    model_config = ConfigDict(arbitrary_types_allowed=True)


# Update forward refs
CreateEvent.model_rebuild()
ViewEvent.model_rebuild()
UpdateEvent.model_rebuild()
