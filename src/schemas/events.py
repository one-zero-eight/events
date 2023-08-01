__all__ = ["CreateEvent", "ViewEvent", "UpdateEvent", "AddEventPatch", "ViewEventPatch", "UpdateEventPatch"]

import datetime
from typing import Optional

from pydantic import BaseModel, Field, validator
from icalendar import vRecur


class CreateEvent(BaseModel):
    name: str
    description: Optional[str] = None
    patches: list["AddEventPatch"] = Field(default_factory=list)


class ViewEvent(BaseModel):
    id: int
    name: str
    description: Optional[str] = None

    patches: list["ViewEventPatch"] = Field(default_factory=list)

    class Config:
        orm_mode = True


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

    @validator("rrule", pre=True)
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

    @validator("rrule", pre=True)
    def _validate_rrule(cls, v):
        if isinstance(v, str):
            return vRecur.from_ical(v)
        return v

    class Config:
        orm_mode = True


class UpdateEventPatch(BaseModel):
    ...


# Update forward refs
CreateEvent.update_forward_refs()
ViewEvent.update_forward_refs()
UpdateEvent.update_forward_refs()
