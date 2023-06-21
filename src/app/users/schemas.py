from typing import Optional

from pydantic import Field, BaseModel


class Group(BaseModel):
    name: str
    type: Optional[str]


class ViewUser(BaseModel):
    """
    Represents a user instance from the database excluding sensitive information.
    """

    email: str
    ru_name: Optional[str]
    groups: list[Group] = Field(default_factory=list)
    favorites: list[str] = Field(default_factory=list)

    class Config:
        orm_mode = True
