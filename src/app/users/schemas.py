from typing import Optional

from pydantic import Field, BaseModel


class ViewGroup(BaseModel):
    name: str
    type: Optional[str] = None
    hidden: Optional[bool] = False

    class Config:
        orm_mode = True


class CreateFavorite(BaseModel):
    name: str
    type: Optional[str] = None
    hidden: Optional[bool] = False


class ViewFavorite(BaseModel):
    name: str
    type: str | None = None
    hidden: bool = False

    class Config:
        orm_mode = True


class CreateUser(BaseModel):
    """
    Represents a user instance to be created.
    """

    email: str
    name: Optional[str] = None
    status: Optional[str] = None
    groups: Optional[list[ViewGroup]] = Field(default_factory=list)
    favorites: Optional[list[ViewFavorite]] = Field(default_factory=list)


class ViewUser(BaseModel):
    """
    Represents a user instance from the database excluding sensitive information.
    """

    email: str
    name: Optional[str] = None
    status: Optional[str] = None
    groups: list[ViewGroup] = Field(default_factory=list)
    favorites: list[ViewFavorite] = Field(default_factory=list)

    class Config:
        orm_mode = True
