from fastapi import APIRouter
from ._types import ID

router = APIRouter(prefix="/search", tags=["Search"])


@router.post("/event-chains")
async def search_event_chains(
    name: str, description: str, schedule: str, owner: str
) -> list[int]:
    ...


@router.post("/event-groups")
async def search_event_group(
    owner_id: str, name: str, description: str, date: str, creator_id: str
) -> list[int]:
    ...
