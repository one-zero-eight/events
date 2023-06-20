from fastapi import APIRouter

from app.schemas import CreateEventGroup
from ._types import ID

router = APIRouter(prefix="/event-groups", tags=["Event Groups"])


@router.patch("/{event-group-id}")
async def update_event_group(user_id: ID, event_group_id: ID):
    ...


@router.post("/")
async def create_event_group(event_group: CreateEventGroup) -> str:
    ...


@router.get("/{event-group-id}/ics")
async def get_ics_from_event_group(event_group_id: ID) -> str:
    ...


@router.post("/{event-group-id}/subscribe")
async def subscribe_user_on_event_group(event_group_id: ID) -> str:
    ...
