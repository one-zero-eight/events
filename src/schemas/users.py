__all__ = ["CreateUser", "ViewUser", "UpdateUser"]

from typing import Optional, Collection

from pydantic import Field, BaseModel, validator

from src.schemas.linked import LinkedCalendarView


class CreateUser(BaseModel):
    """
    Represents a user instance to be created.
    """

    id: Optional[int] = None
    email: str
    name: Optional[str] = None


class ViewUser(BaseModel):
    """
    Represents a user instance from the database excluding sensitive information.
    """

    id: int
    email: str
    name: Optional[str] = None
    favorites_association: list["UserXFavoriteGroupView"] = Field(default_factory=list)
    linked_calendars: dict[str, "LinkedCalendarView"] = Field(default_factory=dict)

    @validator("favorites_association", pre=True)
    def groups_to_list(cls, v):
        if isinstance(v, Collection):
            v = list(v)
        return v

    @validator("linked_calendars", pre=True)
    def calendars_to_dict(cls, v):
        if not isinstance(v, dict):
            keys = [calendar.alias for calendar in v]
            return dict(zip(keys, v))
        return v

    class Config:
        orm_mode = True


class UpdateUser(BaseModel):
    """
    Represents a user instance to be updated.
    """

    email: Optional[str] = None
    name: Optional[str] = None


# fix circular import
from src.schemas.event_groups import UserXFavoriteGroupView  # noqa: E402

ViewUser.update_forward_refs()
