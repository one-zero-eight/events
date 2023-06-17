import time

from schemas import EventChain, UserGroup, EventGroup

from fastapi import APIRouter

router = APIRouter(
    prefix="",
    tags=["Routers"]
)


@router.post("/search/event-chains")
async def search_event_chains(name: str, description: str, schedule: str, owner: str) -> list[int]:
    ...


@router.post("/login")
async def auth_user(email: str, password: str) -> str:
    ...


@router.post("/event-chains")
async def create_event_chain(EventChain) -> str:
    ...


@router.post("/search/event-group")
async def search_event_chains(owner_id: str, name: str, description: str, date: str, creator_id: str) -> list[int]:
    ...


@router.put("/webhook/{webhook_id}")
async def configure_webhook():
    ...


@router.post("/webhooks")
async def create_webhook():
    ...


@router.get("/event-groups/{event-group-id}/ics")
async def get_ics_from_event_group(event_group_id: int) -> str:
    ...


@router.post("/event-groups/{event-group-id}/subscribe")
async def subscribe_user_on_event_group(auth_token: str, user_id: int, event_group_id: int) -> str:
    ...


@router.post("/registration")
async def register_user(email: str, password: str) -> str:
    ...


@router.patch("/user-groups/{user-group-id}")
async def update_user_group(user_id: str, update_user_id: int):
    ...


@router.post("/user-groups")
async def create_user_group(UserGroup) -> str:
    ...


@router.patch("/event-groups/{event-group-id}")
async def update_event_group(user_id: str, event_group_id: str):
    ...


@router.post("/event-groups")
async def create_event_group(EventGroup) -> str:
    ...


@router.put("/event-chains/{event-chain-id}")
async def update_event_chain(EventChain):
    ...
