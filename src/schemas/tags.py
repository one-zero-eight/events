__all__ = ["CreateTag", "ViewTag"]

import json
from typing import Optional

from pydantic import BaseModel, validator, Json, Field

from src.schemas.ownership import Ownership


class CreateTag(BaseModel):
    alias: str
    type: str
    name: Optional[str] = None
    satellite: Optional[Json] = None

    @validator("satellite", pre=True, always=True)
    def _validate_satellite(cls, v):
        if isinstance(v, dict):
            v = json.dumps(v)
        return v


class ViewTag(BaseModel):
    id: int
    alias: str
    type: Optional[str] = None
    name: Optional[str] = None
    satellite: Optional[dict] = None

    ownerships: list[Ownership] = Field(default_factory=list)

    @validator("satellite", pre=True, always=True)
    def _validate_satellite(cls, v):
        if isinstance(v, str):
            return json.loads(v)
        return v

    # @property
    # def owners(self) -> list[ViewUser]:
    #     _owners = []
    #     for ownership in self.ownerships:
    #         if ownership.ownership_enum == OwnershipEnum.owner:
    #             _owners.append(ownership.user)
    #     return _owners
    #
    # @property
    # def moderators(self) -> list[ViewUser]:
    #     _moderators = []
    #     for ownership in self.ownerships:
    #         if ownership.ownership_enum == OwnershipEnum.moderator:
    #             _moderators.append(ownership.user)
    #     return _moderators

    class Config:
        orm_mode = True


Ownership.update_forward_refs()
