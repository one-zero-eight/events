__all__ = [
    "CreateWorkshop",
    "ViewWorkshop",
    "CheckIn",
    "CreateTimeslot",
    "Timeslot",
]

from typing import Optional

from pydantic import BaseModel, Field
import datetime


class CreateWorkshop(BaseModel):
    alias: str
    name: str
    date: datetime.date
    speaker: Optional[str] = None
    capacity: Optional[int] = None
    comment: Optional[str] = None
    location: Optional[str] = None
    timeslots: Optional[list["CreateTimeslot"]] = None


class ViewWorkshop(BaseModel):
    id: int
    alias: str
    name: str
    date: datetime.date
    speaker: Optional[str] = None
    capacity: Optional[int] = None
    comment: Optional[str] = None
    location: Optional[str] = None
    timeslots: list["Timeslot"] = Field(default_factory=list)
    checkin_count: Optional[int] = Field(None, exclude=True)

    class Config:
        orm_mode = True


class CreateTimeslot(BaseModel):
    sequence: Optional[int] = None
    start: datetime.time
    end: datetime.time

    class Config:
        orm_mode = True


class Timeslot(BaseModel):
    workshop_id: int
    sequence: int
    start: datetime.time
    end: datetime.time

    class Config:
        orm_mode = True


class UpdateWorkshop(BaseModel):
    alias: Optional[str] = None
    name: Optional[str] = None
    date: Optional[datetime.date] = None
    speaker: Optional[str] = None
    capacity: Optional[int] = None
    comment: Optional[str] = None
    location: Optional[str] = None
    timeslots: Optional[list["CreateTimeslot"]] = None


class CheckIn(BaseModel):
    workshop_id: int
    user_id: int
    timeslot_sequence: int
    dtstamp: datetime.datetime

    class Config:
        orm_mode = True


from src.schemas.users import ViewUser  # noqa: E402, F401

ViewWorkshop.update_forward_refs()
CreateWorkshop.update_forward_refs()
