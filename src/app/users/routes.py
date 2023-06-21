from typing import Annotated
from fastapi import APIRouter, Depends
from src.app.dependencies import get_user_repository, UserRepository
from src.app.users.schemas import ViewUser

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/", response_model=list[ViewUser])
async def get_users(user_repository: Annotated[UserRepository, Depends(get_user_repository)]):
    return [ViewUser.from_orm(user) for user in user_repository.get_users()]
