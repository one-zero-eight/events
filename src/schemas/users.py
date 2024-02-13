__all__ = ["CreateUser", "ViewUser", "UpdateUser", "ViewUserScheduleKey"]

from typing import Optional, Collection

from pydantic import Field, BaseModel, field_validator, ConfigDict

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

    @field_validator("favorites_association", mode="before")
    def groups_to_list(cls, v):
        if isinstance(v, Collection):
            v = list(v)
        return v

    @field_validator("linked_calendars", mode="before")
    def calendars_to_dict(cls, v):
        if not isinstance(v, dict):
            keys = [calendar.alias for calendar in v]
            return dict(zip(keys, v))
        return v

    model_config = ConfigDict(from_attributes=True)


class ViewUserScheduleKey(BaseModel):
    """
    Represents a user schedule key.
    """

    user_id: int
    access_key: str
    resource_path: str


class UpdateUser(BaseModel):
    """
    Represents a user instance to be updated.
    """

    email: Optional[str] = None
    name: Optional[str] = None


# fix circular import
from src.schemas.event_groups import UserXFavoriteGroupView  # noqa: E402

ViewUser.update_forward_refs()
