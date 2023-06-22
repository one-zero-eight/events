from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from src.app.dependencies import get_user_repository, get_current_user_email
from src.app.users.schemas import ViewUser
from src.repositories import UserRepository

router = APIRouter(prefix="/users", tags=["Users"])


@router.get(
    "/me",
    responses={
        200: {"description": "Current user info", "model": ViewUser},
        401: {"description": "User is not authenticated"},
        404: {"description": "User not found"},
    },
)
async def get_me(
        email: Annotated[str, Depends(get_current_user_email)],
        user_repository: Annotated[UserRepository, Depends(get_user_repository)],
):
    """
    Get current user info if authenticated
    """
    try:
        current_user = user_repository.get_user_by_email(email)

        return ViewUser.from_orm(current_user)
    except ValueError as e:
        raise HTTPException(status_code=404, detail="User not found")


@router.post(
    "/me/favorites",
    responses={
        200: {"description": "Favorite added"},
    }
)
async def add_favorite(
        email: Annotated[str, Depends(get_current_user_email)],
        user_repository: Annotated[UserRepository, Depends(get_user_repository)],
        favorites: list[str],
):
    """
    Add favorite to current user
    """
    try:
        user_repository.extend_favorites(email, *favorites)
    except ValueError:
        raise HTTPException(status_code=404, detail="User not found")
