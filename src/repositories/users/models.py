from typing import Optional

from pydantic import BaseModel, Field


class InJsonGroup(BaseModel):
    """
    Represents a group instance from the database including sensitive information.
    """

    name: str
    type: Optional[str]
    hidden: Optional[bool] = False


class InJsonFavorite(BaseModel):
    """
    Represents a favorite instance from the database including sensitive information.
    """

    name: str
    type: Optional[str]
    hidden: Optional[bool] = False


class InJsonUser(BaseModel):
    """
    Represents a user instance from the database including sensitive information.
    """

    email: str
    groups: list[InJsonGroup] = Field(default_factory=list)
    favorites: list[InJsonFavorite] = Field(default_factory=list)

    name: str | None = Field(alias="commonname")
    status: str | None = Field(alias="Status")
