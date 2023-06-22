from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from src.app.dependencies import get_user_repository, get_current_user_email
from src.app.users.schemas import ViewUser
from src.repositories import UserRepository

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=ViewUser)
async def get_me(
    email: Annotated[str, Depends(get_current_user_email)],
    user_repository: Annotated[UserRepository, Depends(get_user_repository)],
):
    try:
        current_user = user_repository.get_user_by_email(email)
        return ViewUser.from_orm(current_user)
    except ValueError:
        raise HTTPException(status_code=404, detail="User not found")
