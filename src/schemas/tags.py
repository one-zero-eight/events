__all__ = ["CreateTag", "ViewTag", "TagOwnership", "OwnershipEnum"]

import json
from enum import StrEnum
from typing import Optional

from pydantic import BaseModel, validator, Json, Field


class CreateTag(BaseModel):
    name: str = None
    type: str
    satellite: Optional[Json] = None

    @validator("satellite", pre=True, always=True)
    def _validate_satellite(cls, v):
        if isinstance(v, dict):
            v = json.dumps(v)
        return v


class OwnershipEnum(StrEnum):
    default = "default"
    moderator = "moderator"
    owner = "owner"


class TagOwnership(BaseModel):
    user_id: int
    tag_id: int

    ownership_enum: OwnershipEnum

    @validator("ownership_enum", pre=True, always=True)
    def _validate_ownership_enum(cls, v):
        return OwnershipEnum(v)

    class Config:
        orm_mode = True


class ViewTag(BaseModel):
    id: int
    name: str
    type: Optional[str] = None
    satellite: Optional[dict] = None

    ownership_association: list[TagOwnership] = Field(default_factory=list)

    @validator("satellite", pre=True, always=True)
    def _validate_satellite(cls, v):
        if isinstance(v, str):
            return json.loads(v)
        return v

    # @property
    # def owners(self) -> list[ViewUser]:
    #     _owners = []
    #     for ownership in self.ownership_association:
    #         if ownership.ownership_enum == OwnershipEnum.owner:
    #             _owners.append(ownership.user)
    #     return _owners
    #
    # @property
    # def moderators(self) -> list[ViewUser]:
    #     _moderators = []
    #     for ownership in self.ownership_association:
    #         if ownership.ownership_enum == OwnershipEnum.moderator:
    #             _moderators.append(ownership.user)
    #     return _moderators

    class Config:
        orm_mode = True


TagOwnership.update_forward_refs()
