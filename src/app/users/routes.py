from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from starlette import status

from src.app.dependencies import get_user_repository, get_current_user_email
from src.app.users.schemas import ViewUser, CreateFavorite, ViewFavorite
from src.repositories import UserRepository

router = APIRouter(prefix="/users", tags=["Users"])

auth_responses_schema = {
    401: {"description": "User is not authenticated"},
    404: {"description": "User not found"},
}


@router.get(
    "/me",
    responses={
        200: {"description": "Current user info", "model": ViewUser},
        **auth_responses_schema,
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
        200: {"description": "Favorite added successfully"},
        **auth_responses_schema,
    },
)
async def add_favorite(
    email: Annotated[str, Depends(get_current_user_email)],
    user_repository: Annotated[UserRepository, Depends(get_user_repository)],
    favorite: CreateFavorite,
) -> list[ViewFavorite]:
    """
    Add favorite to current user
    """
    try:
        updated_favorites = user_repository.extend_favorites(email, favorite)
        return [ViewFavorite.from_orm(fav) for fav in updated_favorites]
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )


@router.delete(
    "/me/favorites",
    responses={
        200: {"description": "Favorite deleted"},
        **auth_responses_schema,
    },
)
async def delete_favorite(
    email: Annotated[str, Depends(get_current_user_email)],
    user_repository: Annotated[UserRepository, Depends(get_user_repository)],
    favorite: str,
) -> list[ViewFavorite]:
    """
    Delete favorite from current user
    """
    try:
        updated_favorites = user_repository.delete_favorites(email, favorite)
        return [ViewFavorite.from_orm(fav) for fav in updated_favorites]
    except ValueError:
        raise HTTPException(status_code=404, detail="User not found")


# TODO: Implement hiding\unhiding favorites and groups
# @router.post("/me/favorites/hidden", responses={
#     200: {"description": "Favorite hidden"},
#     **auth_responses_schema,
# })
# async def hide_favorite(
#         email: Annotated[str, Depends(get_current_user_email)],
#         user_repository: Annotated[UserRepository, Depends(get_user_repository)],
#         favorite: str,
# ) -> list[ViewFavorite]:
#     """
#     Hide favorite from current user
#     """
#     try:
#         updated_favorites = user_repository.hide_favorites(email, favorite)
#         return [ViewFavorite.from_orm(fav) for fav in updated_favorites]
#     except ValueError:
#         raise HTTPException(status_code=404, detail="User not found")
