from typing import Annotated, Iterable

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from src.app.auth.dependencies import get_current_user_email
from src.app.schemas import ViewUser, CreateEventGroup, UserXGroupView
from src.exceptions import UserNotFoundException
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
    user_id = await user_repository.get_user_id_by_email(email)

    if user_id is None:
        raise UserNotFoundException()

    return await user_repository.get_user(user_id)


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
    user_id = await user_repository.get_user_id_by_email(email)

    if user_id is None:
        raise UserNotFoundException()

    group = await user_repository.create_group_if_not_exists(favorite)

    updated_favorites = await user_repository.add_favorite(user_id, group.id)
    return ListOfFavorites.from_iterable(updated_favorites)


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
    group_id: int,
) -> ListOfFavorites:
    """
    Delete favorite from current user
    """
    user_id = await user_repository.get_user_id_by_email(email)

    if user_id is None:
        raise UserNotFoundException()

    # check if group exists
    if await user_repository.get_group(group_id) is None:
        raise UserNotFoundException()

    updated_favorites = await user_repository.remove_favorite(user_id, group_id)
    return ListOfFavorites.from_iterable(updated_favorites)


@router.post(
    "/me/favorites/hide",
    responses={
        200: {"description": "Favorite hidden"},
        **auth_responses_schema,
    },
)
async def hide_favorite(
    email: Annotated[str, Depends(get_current_user_email)],
    user_repository: Annotated[
        AbstractUserRepository, Depends(Dependencies.get_user_repository)
    ],
    group_id: int,
    hide: bool = True,
) -> ListOfFavorites:
    """
    Hide favorite from current user
    """
    user_id = await user_repository.get_user_id_by_email(email)

    if user_id is None:
        raise UserNotFoundException()

    # check if group exists
    if await user_repository.get_group(group_id) is None:
        raise UserNotFoundException()

    updated_favorites = await user_repository.set_hidden(
        user_id=user_id, group_id=group_id, hide=hide, is_favorite=True
    )

    return ListOfFavorites.from_iterable(updated_favorites)


@router.post(
    "/me/groups/hide",
    responses={
        200: {"description": "Group hidden"},
        **auth_responses_schema,
    },
)
async def hide_group(
    email: Annotated[str, Depends(get_current_user_email)],
    user_repository: Annotated[
        AbstractUserRepository, Depends(Dependencies.get_user_repository)
    ],
    group_id: int,
    hide: bool = True,
) -> ListOfFavorites:
    """
    Hide group from current user
    """
    user_id = await user_repository.get_user_id_by_email(email)

    if user_id is None:
        raise UserNotFoundException()

    # check if group exists
    if await user_repository.get_group(group_id) is None:
        raise UserNotFoundException()

    updated_favorites = await user_repository.set_hidden(
        user_id=user_id, group_id=group_id, hide=hide, is_favorite=False
    )

    return ListOfFavorites.from_iterable(updated_favorites)
