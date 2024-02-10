from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError

from src.app.dependencies import (
    CURRENT_USER_ID_DEPENDENCY,
    Shared,
)
from src.app.users import router
from src.exceptions import (
    UserNotFoundException,
    IncorrectCredentialsException,
    NoCredentialsException,
    DBEventGroupDoesNotExistInDb,
    EventGroupNotFoundException,
)
from src.repositories.event_groups import SqlEventGroupRepository
from src.repositories.users import SqlUserRepository
from src.schemas import ViewUser
from src.schemas.linked import LinkedCalendarView, LinkedCalendarCreate


@router.get(
    "/me",
    responses={
        200: {"description": "Current user info"},
        **IncorrectCredentialsException.responses,
        **NoCredentialsException.responses,
    },
)
async def get_me(
    user_id: CURRENT_USER_ID_DEPENDENCY,
) -> ViewUser:
    """
    Get current user info if authenticated
    """
    user_repository = Shared.f(SqlUserRepository)
    user = await user_repository.read(user_id)
    return user


@router.post(
    "/me/favorites",
    responses={
        200: {"description": "Favorite added successfully"},
        **EventGroupNotFoundException.responses,
        **IncorrectCredentialsException.responses,
        **NoCredentialsException.responses,
    },
)
async def add_favorite(
    user_id: CURRENT_USER_ID_DEPENDENCY,
    group_id: int,
) -> ViewUser:
    """
    Add favorite to current user
    """
    try:
        user_repository = Shared.f(SqlUserRepository)
        updated_user = await user_repository.add_favorite(user_id, group_id)
        return updated_user
    except DBEventGroupDoesNotExistInDb as e:
        raise EventGroupNotFoundException() from e


@router.delete(
    "/me/favorites",
    responses={
        200: {"description": "Favorite deleted"},
        **IncorrectCredentialsException.responses,
        **NoCredentialsException.responses,
    },
)
async def delete_favorite(
    user_id: CURRENT_USER_ID_DEPENDENCY,
    group_id: int,
) -> ViewUser:
    """
    Delete favorite from current user
    """
    user_repository = Shared.f(SqlUserRepository)
    updated_user = await user_repository.remove_favorite(user_id, group_id)
    return updated_user


@router.post(
    "/me/favorites/hide",
    responses={
        200: {"description": "Favorite hidden"},
        **IncorrectCredentialsException.responses,
        **NoCredentialsException.responses,
    },
)
async def hide_favorite(
    user_id: CURRENT_USER_ID_DEPENDENCY,
    group_id: int,
    hide: bool = True,
) -> ViewUser:
    """
    Hide favorite from current user
    """
    # check if a group exists
    event_group_repository = Shared.f(SqlEventGroupRepository)
    if await event_group_repository.read(group_id) is None:
        raise UserNotFoundException()
    user_repository = Shared.f(SqlUserRepository)
    updated_user = await user_repository.set_hidden(user_id=user_id, group_id=group_id, hide=hide)
    return updated_user


@router.post(
    "/me/linked",
    responses={
        200: {"description": "Linked calendar added successfully"},
        **IncorrectCredentialsException.responses,
        **NoCredentialsException.responses,
    },
)
async def link_calendar(
    linked_calendar: LinkedCalendarCreate,
    user_id: CURRENT_USER_ID_DEPENDENCY,
) -> LinkedCalendarView:
    """
    Add linked calendar to current user
    """
    try:
        user_repository = Shared.f(SqlUserRepository)
        calendar = await user_repository.link_calendar(user_id, linked_calendar)
        return calendar
    except IntegrityError:
        raise HTTPException(status_code=409, detail="Calendar with this alias already exists")
