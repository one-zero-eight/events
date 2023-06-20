from fastapi import APIRouter

from src.app.schemas import UserGroup
from ._types import ID

router = APIRouter(prefix="/user-groups", tags=["User Groups"])


@router.patch("/{user-group-id}")
async def update_user_group(user_group_id: ID):
    ...


@router.post("/")
async def create_user_group(user_group: UserGroup) -> str:
    ...
