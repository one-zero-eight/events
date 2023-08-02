__all__ = ["setup_ownership_method"]

from sqlalchemy import delete
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from src.schemas import OwnershipEnum


async def setup_ownership_method(
    cls, session: AsyncSession, object_id: int, user_id: int, role_alias: OwnershipEnum
) -> None:
    OwnershipClass = cls.Ownership

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
