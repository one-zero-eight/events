from typing import Optional

from pydantic import Field, BaseModel


class ViewGroup(BaseModel):
    name: str
    type: Optional[str]
    hidden: Optional[bool] = False

    class Config:
        orm_mode = True


class CreateFavorite(BaseModel):
    name: str
    type: Optional[str] = None
    hidden: Optional[bool] = False


class ViewFavorite(BaseModel):
    name: str
    type: Optional[str]
    hidden: bool = False

    class Config:
        orm_mode = True


class CreateUser(BaseModel):
    """
    Represents a user instance to be created.
    """

    email: str
    name: Optional[str]
    status: Optional[str]
    groups: Optional[list[ViewGroup]]
    favorites: Optional[list[ViewFavorite]]


class ViewUser(BaseModel):
    """
    Represents a user instance from the database excluding sensitive information.
    """

    email: str
    name: Optional[str]
    status: Optional[str]
    groups: list[ViewGroup] = Field(default_factory=list)
    favorites: list[ViewFavorite] = Field(default_factory=list)

    class Config:
        orm_mode = True
