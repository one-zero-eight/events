from src.api.workshops import router
from src.schemas import ViewWorkshop, CheckIn
from src.api.dependencies import (
    CURRENT_USER_ID_DEPENDENCY,
)
from pydantic import BaseModel


class ListWorkshopsResponse(BaseModel):
    workshops: list[ViewWorkshop]


class ListCheckInResponse(BaseModel):
    check_ins: list[CheckIn]


@router.get(
    "/",
    responses={
        200: {"description": "List of all workshops"},
    },
)
async def list_workshops() -> ListWorkshopsResponse:
    """
    List all workshops
    """
    raise NotImplementedError()


@router.get(
    "/user-check-in/",
    responses={
        200: {"description": "List of all workshops current user checked in"},
    },
)
async def list_workshops_user_check_in() -> ListCheckInResponse:
    """
    List all checkins for current user
    """
    raise NotImplementedError()


@router.get(
    "/{workshop_id}",
    responses={
        200: {"description": "Workshop info"},
    },
)
async def get_workshop(workshop_id: int) -> ViewWorkshop:
    """
    Get workshop info
    """
    raise NotImplementedError()


@router.put(
    "/{workshop_id}/?check_in={check_in}",
    responses={
        201: {"description": "Check-in or Check-out successful"},
    },
    status_code=201,
)
async def check_in(
    workshop_id: int,
    user_id: CURRENT_USER_ID_DEPENDENCY,
    check_in: bool = True,
) -> None:
    """
    Check-in or Check-out from workshop
    """
    raise NotImplementedError()
