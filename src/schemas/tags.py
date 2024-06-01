__all__ = ["CreateTag", "ViewTag", "UpdateTag"]

import json
from typing import Optional

from pydantic import BaseModel, Json, ConfigDict, field_validator

from src.schemas.ownership import Ownership


class CreateTag(BaseModel, frozen=True):
    alias: str
    type: Optional[str] = None
    name: Optional[str] = None
    satellite: Optional[Json] = None

    @field_validator("satellite", mode="before")
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

    # ownerships: list[Ownership] = Field(default_factory=list)
    @field_validator("satellite", mode="before")
    def _validate_satellite(cls, v):
        if isinstance(v, str):
            return json.loads(v)
        return v

    model_config = ConfigDict(from_attributes=True)


class UpdateTag(BaseModel):
    alias: Optional[str] = None
    type: Optional[str] = None
    name: Optional[str] = None
    satellite: Optional[Json] = None

    @field_validator("satellite", mode="before")
    def _validate_satellite(cls, v):
        if isinstance(v, dict):
            v = json.dumps(v)
        return v


Ownership.update_forward_refs()
