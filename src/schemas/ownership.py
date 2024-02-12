from enum import StrEnum

from pydantic import ConfigDict, BaseModel, field_validator


class OwnershipEnum(StrEnum):
    default = "default"
    moderator = "moderator"
    owner = "owner"
    delete = "delete"


class Ownership(BaseModel):
    user_id: int
    object_id: int

    role_alias: OwnershipEnum

    @field_validator("role_alias", mode="before")
    def _validate_ownership_enum(cls, v):
        return OwnershipEnum(v)

    model_config = ConfigDict(from_attributes=True)
