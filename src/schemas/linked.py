__all__ = ["LinkedCalendarView", "LinkedCalendarCreate", "LinkedCalendarUpdate"]


from typing import Optional


from pydantic import BaseModel


class LinkedCalendarView(BaseModel):
    """
    Represents a linked calendar instance from the database excluding sensitive information.
    """

    id: int
    user_id: int
    alias: str
    url: str
    name: Optional[str] = None
    description: Optional[str] = None
    color: Optional[str] = None
    is_active: bool = True

    class Config:
        orm_mode = True


class LinkedCalendarCreate(BaseModel):
    """
    Represents a linked calendar instance to be created.
    """

    alias: str
    url: str
    name: Optional[str] = None
    description: Optional[str] = None
    color: Optional[str] = None
    is_active: bool = True


class LinkedCalendarUpdate(BaseModel):
    """
    Represents a linked calendar instance to be updated.
    """

    alias: Optional[str] = None
    url: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    color: Optional[str] = None
    is_active: Optional[bool] = None
