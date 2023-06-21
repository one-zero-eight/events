from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from src.app.dependencies import get_user_repository, get_current_user_email
from src.app.users.schemas import ViewUser
from src.repositories.users.repository import UserRepository

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/", response_model=list[ViewUser])
async def get_users(
    user_repository: Annotated[UserRepository, Depends(get_user_repository)]
):
    return [ViewUser.from_orm(user) for user in user_repository.get_users()]


@router.get("/me", response_model=ViewUser)
async def get_me(
    email: Annotated[str, Depends(get_current_user_email)],
    user_repository: Annotated[UserRepository, Depends(get_user_repository)],
):
    try:
        return ViewUser.from_orm(user_repository.get_user_by_email(email))
    except ValueError:
        raise HTTPException(status_code=404, detail="User not found")
