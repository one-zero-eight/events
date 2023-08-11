__all__ = ["CreateTag", "ViewTag", "UpdateTag"]

import json
from typing import Optional

from pydantic import BaseModel, validator, Json, Field

from src.schemas.ownership import Ownership


class CreateTag(BaseModel):
    alias: str
    type: Optional[str] = None
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

    class Config:
        orm_mode = True


class UpdateTag(BaseModel):
    alias: Optional[str] = None
    type: Optional[str] = None
    name: Optional[str] = None
    satellite: Optional[Json] = None

    @validator("satellite", pre=True, always=True)
    def _validate_satellite(cls, v):
        if isinstance(v, dict):
            v = json.dumps(v)
        return v


Ownership.update_forward_refs()
