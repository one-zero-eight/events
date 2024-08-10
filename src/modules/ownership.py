__all__ = ["setup_ownership_method", "Ownership", "OwnershipEnum"]

from enum import StrEnum

from pydantic import BaseModel, field_validator, ConfigDict
from sqlalchemy import delete
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession


class OwnershipEnum(StrEnum):
    default = "default"
    moderator = "moderator"
    owner = "owner"
    delete = "delete"


async def setup_ownership_method(
    OwnershipClass, session: AsyncSession, object_id: int, user_id: int, role_alias: OwnershipEnum
) -> None:
    if role_alias is OwnershipEnum.delete:
        # just delete row
        q = delete(OwnershipClass).where(OwnershipClass.user_id == user_id).where(OwnershipClass.object_id == object_id)
        await session.execute(q)
    else:
        # insert or update
        q = insert(OwnershipClass).values(
            user_id=user_id,
            object_id=object_id,
            role_alias=role_alias,
        )
        q = q.on_conflict_do_update(
            index_elements=[OwnershipClass.user_id, OwnershipClass.object_id],
            set_={"role_alias": role_alias.value},
        )
        await session.execute(q)
    await session.commit()


class Ownership(BaseModel):
    user_id: int
    object_id: int

    role_alias: OwnershipEnum

    @field_validator("role_alias", mode="before")
    def _validate_ownership_enum(cls, v):
        return OwnershipEnum(v)

    model_config = ConfigDict(from_attributes=True)
