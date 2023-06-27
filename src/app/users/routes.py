from typing import Annotated, Iterable

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from starlette import status

from src.app.auth.dependencies import get_current_user_email
from src.app.schemas import ViewUser, CreateEventGroup, UserXGroupView
from src.repositories.dependencies import Dependencies
from src.repositories.users import AbstractUserRepository

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
    user_repository: Annotated[
        AbstractUserRepository, Depends(Dependencies.get_user_repository)
    ],
) -> ViewUser:
    """
    Get current user info if authenticated
    """
    try:
        return await user_repository.get_user_by_email(email)
    except ValueError:
        raise HTTPException(status_code=404, detail="User not found")


class ListOfFavorites(BaseModel):
    favorites: list[UserXGroupView]

    @classmethod
    def from_iterable(cls, favorites: Iterable[UserXGroupView]) -> "ListOfFavorites":
        return cls(favorites=list(favorites))


@router.post(
    "/me/favorites",
    responses={
        200: {"description": "Favorite added successfully"},
        **auth_responses_schema,
    },
)
async def add_favorite(
    email: Annotated[str, Depends(get_current_user_email)],
    user_repository: Annotated[
        AbstractUserRepository, Depends(Dependencies.get_user_repository)
    ],
    favorite: CreateEventGroup,
) -> ListOfFavorites:
    """
    Add favorite to current user
    """
    try:
        updated_favorites = await user_repository.add_favorite(email, favorite)
        return ListOfFavorites.from_iterable(updated_favorites)
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
    user_repository: Annotated[
        AbstractUserRepository, Depends(Dependencies.get_user_repository)
    ],
    favorite: CreateEventGroup,
) -> ListOfFavorites:
    """
    Delete favorite from current user
    """
    try:
        updated_favorites = await user_repository.remove_favorite(email, favorite)
        return ListOfFavorites.from_iterable(updated_favorites)
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
# ) -> list[ViewEventGroup]:
#     """
#     Hide favorite from current user
#     """
#     try:
#         updated_favorites = user_repository.hide_favorites(email, favorite)
#         return [ViewEventGroup.from_orm(fav) for fav in updated_favorites]
#     except ValueError:
#         raise HTTPException(status_code=404, detail="User not found")
