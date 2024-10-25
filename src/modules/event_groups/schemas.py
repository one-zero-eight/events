__all__ = [
    "CreateEventGroupWithoutTags",
    "CreateEventGroup",
    "ViewEventGroup",
    "UpdateEventGroup",
    "ListEventGroupsResponse",
]

import datetime
from typing import Iterable, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

from src.modules.tags.schemas import CreateTag, ViewTag


class CreateEventGroupWithoutTags(BaseModel):
    """
    Represents a group instance to be created.
    """

    alias: str
    name: str
    path: Optional[str] = None
    description: Optional[str] = None


class CreateEventGroup(CreateEventGroupWithoutTags):
    tags: list[CreateTag] = Field(default_factory=list)


class ViewEventGroup(BaseModel):
    """
    Represents a group instance from the database excluding sensitive information.
    """

    id: int
    alias: str
    updated_at: datetime.datetime
    created_at: datetime.datetime
    path: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    tags: list[ViewTag] = Field(default_factory=list)

    # ownerships: list["Ownership"] = Field(default_factory=list)
    @field_validator("tags", mode="before")
    def _validate_tags(cls, v):
        v = list(v) if v else []
        return v

    model_config = ConfigDict(from_attributes=True)


class UpdateEventGroup(BaseModel):
    """
    Represents a group instance to be updated.
    """

    alias: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    path: Optional[str] = None


class ListEventGroupsResponse(BaseModel):
    """
    Represents a list of event groups.
    """

    event_groups: list[ViewEventGroup]

    @classmethod
    def from_iterable(cls, groups: Iterable[ViewEventGroup]) -> "ListEventGroupsResponse":
        return cls(event_groups=groups)
