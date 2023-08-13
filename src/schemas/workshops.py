__all__ = [
    "CreateWorkshop",
    "ViewWorkshop",
    "CheckIn",
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
    timeslots: list[tuple[datetime.time, datetime.time]] = Field(..., min_items=1)


class ViewWorkshop(BaseModel):
    id: int
    alias: str
    name: str
    date: datetime.date
    speaker: Optional[str] = None
    capacity: Optional[int] = None
    comment: Optional[str] = None
    location: Optional[str] = None
    timeslots: list[tuple[datetime.time, datetime.time]] = Field(..., min_items=1)
    checkin_count: int = 0

    class Config:
        orm_mode = True


class CheckIn(BaseModel):
    workshop_id: int
    user_id: int
    timeslot_sequence: int
    dtstamp: datetime.datetime

    class Config:
        orm_mode = True


from src.schemas.users import ViewUser  # noqa: E402, F401

ViewWorkshop.update_forward_refs()
