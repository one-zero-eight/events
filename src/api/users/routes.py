from typing import Literal

from fastapi import APIRouter
from fastapi import HTTPException
from pydantic import BaseModel
from sqlalchemy.exc import IntegrityError

from src.api.dependencies import CURRENT_USER_ID_DEPENDENCY
from src.exceptions import IncorrectCredentialsException, NoCredentialsException
from src.exceptions import ObjectNotFound, DBEventGroupDoesNotExistInDb, EventGroupNotFoundException
from src.repositories.event_groups.repository import event_group_repository
from src.repositories.predefined.repository import predefined_repository
from src.repositories.users.repository import user_repository
from src.schemas import ViewUser
from src.schemas.linked import LinkedCalendarView, LinkedCalendarCreate
from src.schemas.users import ViewUserScheduleKey

router = APIRouter(
    prefix="/users",
    tags=["Users"],
    responses={
        **IncorrectCredentialsException.responses,
        **NoCredentialsException.responses,
    },
)


@router.get("/me", responses={200: {"description": "Current user info"}})
async def get_me(user_id: CURRENT_USER_ID_DEPENDENCY) -> ViewUser:
    """
    Get current user info if authenticated
    """

    user = await user_repository.read(user_id)
    return user


class UserPredefinedGroupsResponse(BaseModel):
    event_groups: list[int]


@router.get("/me/predefined", responses={200: {"description": "Predefined event groups for user"}})
async def get_predefined(user_id: CURRENT_USER_ID_DEPENDENCY) -> UserPredefinedGroupsResponse:
    """
    Get predefined event groups for user
    """

    groups = await predefined_repository.get_user_predefined(user_id)
    return UserPredefinedGroupsResponse(event_groups=groups)


@router.post(
    "/me/favorites",
    responses={200: {"description": "Favorite added successfully"}, **EventGroupNotFoundException.responses},
)
async def add_favorite(user_id: CURRENT_USER_ID_DEPENDENCY, group_id: int) -> ViewUser:
    """
    Add favorite to current user
    """
    try:
        updated_user = await user_repository.add_favorite(user_id, group_id)
        return updated_user
    except DBEventGroupDoesNotExistInDb as e:
        raise EventGroupNotFoundException() from e


@router.delete(
    "/me/favorites",
    responses={200: {"description": "Favorite deleted"}},
)
async def delete_favorite(user_id: CURRENT_USER_ID_DEPENDENCY, group_id: int) -> ViewUser:
    """
    Delete favorite from current user
    """

    updated_user = await user_repository.remove_favorite(user_id, group_id)
    return updated_user


@router.post("/me/favorites/hide", responses={200: {"description": "Favorite hidden"}})
async def hide_favorite(user_id: CURRENT_USER_ID_DEPENDENCY, group_id: int, hide: bool = True) -> ViewUser:
    """
    Hide favorite from current user
    """
    # check if a group exists

    if await event_group_repository.read(group_id) is None:
        raise ObjectNotFound(f"Event group with id {group_id} does not exist")

    updated_user = await user_repository.set_hidden_event_group(user_id=user_id, group_id=group_id, hide=hide)
    return updated_user


@router.post("/me/{target}/hide", responses={200: {"description": "Target hidden"}})
async def hide_target(
    user_id: CURRENT_USER_ID_DEPENDENCY, target: Literal["music-room", "sports", "moodle"], hide: bool = True
) -> ViewUser:
    """
    Hide music room, sports or moodle from current user
    """

    updated_user = await user_repository.set_hidden(user_id=user_id, target=target, hide=hide)
    return updated_user


@router.post(
    "/me/linked",
    responses={200: {"description": "Linked calendar added successfully"}},
)
async def link_calendar(
    linked_calendar: LinkedCalendarCreate, user_id: CURRENT_USER_ID_DEPENDENCY
) -> LinkedCalendarView:
    """
    Add linked calendar to current user
    """
    try:
        calendar = await user_repository.link_calendar(user_id, linked_calendar)
        return calendar
    except IntegrityError:
        raise HTTPException(status_code=409, detail="Calendar with this alias already exists")


class _GetScheduleAccessKeyResponse(BaseModel):
    new: bool
    access_key: ViewUserScheduleKey


@router.post(
    "/me/get-schedule-access-key",
    responses={200: {"description": "Schedule access key for given resource"}},
)
async def generate_user_schedule_key(
    resource_path: str, user_id: CURRENT_USER_ID_DEPENDENCY
) -> _GetScheduleAccessKeyResponse:
    """
    Generate an access key for the user schedule
    """

    key = await user_repository.get_user_schedule_key_for_resource(user_id, resource_path)
    new = False
    if key is None:
        key = await user_repository.generate_user_schedule_key(user_id, resource_path)
        new = True
    return _GetScheduleAccessKeyResponse(new=new, access_key=key)


@router.get(
    "/me/schedule-access-keys",
    responses={200: {"description": "Schedule access keys for user"}},
)
async def get_user_schedule_keys(user_id: CURRENT_USER_ID_DEPENDENCY) -> list[ViewUserScheduleKey]:
    """
    Get all access keys for the user schedule
    """

    keys = await user_repository.get_user_schedule_keys(user_id)
    return keys


@router.delete(
    "/me/schedule-access-key",
    responses={
        200: {"description": "Schedule access key deleted"},
    },
)
async def delete_user_schedule_key(access_key: str, resource_path: str, user_id: CURRENT_USER_ID_DEPENDENCY) -> None:
    """
    Delete an access key for the user schedule
    """

    await user_repository.delete_user_schedule_key(user_id, access_key, resource_path)
    return
