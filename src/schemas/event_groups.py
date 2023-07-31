__all__ = [
    "CreateEventGroup",
    "ViewEventGroup",
    "UpdateEventGroup",
    "ListEventGroupsResponse",
    "UserXFavoriteGroupView",
]

from typing import Optional, Iterable

from pydantic import BaseModel, Field, validator


class CreateEventGroup(BaseModel):
    """
    Represents a group instance to be created.
    """

    path: str
    name: Optional[str] = None
    description: Optional[str] = None


class ViewEventGroup(BaseModel):
    """
    Represents a group instance from the database excluding sensitive information.
    """

    id: int
    path: str
    name: Optional[str] = None
    description: Optional[str] = None
    tags: list["ViewTag"] = Field(default_factory=list)

    @validator("tags", pre=True, always=True)
    def _validate_tags(cls, v):
        v = list(v)
        if not isinstance(v, list):
            return []
        return v

    class Config:
        orm_mode = True


class UpdateEventGroup(BaseModel):
    """
    Represents a group instance to be updated.
    """

    name: Optional[str] = None
    description: Optional[str] = None
    path: Optional[str] = None


class UserXFavoriteGroupView(BaseModel):
    """
    Represents a group instance from the database excluding sensitive information.
    """

    user_id: int
    event_group: ViewEventGroup
    hidden: bool
    predefined: bool = False

    class Config:
        orm_mode = True


class ListEventGroupsResponse(BaseModel):
    """
    Represents a list of event groups.
    """

    groups: list[ViewEventGroup]

    @classmethod
    def from_iterable(cls, groups: Iterable[ViewEventGroup]) -> "ListEventGroupsResponse":
        return cls(groups=groups)


from src.schemas.tags import ViewTag  # noqa E402

ViewEventGroup.update_forward_refs()
