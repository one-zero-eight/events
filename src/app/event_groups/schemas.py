from typing import Optional

from pydantic import BaseModel


class CreateEventGroup(BaseModel):
    """
    Represents a group instance to be created.
    """

    name: str
    type: Optional[str] = None


class ViewEventGroup(BaseModel):
    """
    Represents a group instance from the database excluding sensitive information.
    """

    id: int
    name: str
    type: Optional[str] = None

    class Config:
        orm_mode = True


class UserXGroupView(BaseModel):
    """
    Represents a group instance from the database excluding sensitive information.
    """

    user_id: int
    group: ViewEventGroup
    hidden: bool

    class Config:
        orm_mode = True
