__all__ = ["CreateUser", "ViewUser"]

from typing import Optional, Collection

from pydantic import Field, BaseModel, validator


class CreateUser(BaseModel):
    """
    Represents a user instance to be created.
    """

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

    @validator("favorites_association", pre=True)
    def groups_to_list(cls, v):
        if isinstance(v, Collection):
            v = list(v)
        return v

    class Config:
        orm_mode = True


# fix circular import
from src.schemas.event_groups import UserXFavoriteGroupView  # noqa: E402

ViewUser.update_forward_refs()
