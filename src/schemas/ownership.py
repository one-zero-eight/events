from enum import StrEnum

from pydantic import BaseModel, validator


class OwnershipEnum(StrEnum):
    default = "default"
    moderator = "moderator"
    owner = "owner"
    delete = "delete"


class Ownership(BaseModel):
    user_id: int
    object_id: int

    role_alias: OwnershipEnum

    @validator("role_alias", pre=True, always=True)
    def _validate_ownership_enum(cls, v):
        return OwnershipEnum(v)

    class Config:
        orm_mode = True
