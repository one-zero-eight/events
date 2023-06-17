from fastapi import APIRouter

router = APIRouter(
    prefix="/routers",
    tags=["Routers"]
)


@router.post("search/event-chains")
async def search_event_chains():
    ...


@router.post("login")
async def auth():
    ...


@router.post("event-chains")
async def create_event_chain():
    ...


@router.post("search/event-group")
async def search_event_chains():
    ...


@router.put("webhook/{webhook_id}")
async def configure_webhook():
    ...


@router.post("webhooks")
async def create_webhook():
    ...


@router.get("event-groups/{event-group-id}/ics")
async def get_ics_from_event_group():
    ...


@router.post("event-groups/{event-group-id}/subscribe")
async def subscribe_user_on_event_group():
    ...


@router.post("registration")
async def register_user():
    ...


@router.patch("user-groups/{user-group-id}")
async def update_user_group():
    ...


@router.post("user-groups")
async def create_user_group():
    ...


@router.patch("event-groups/{event-group-id}")
async def update_event_group():
    ...


@router.post("event-groups")
async def create_event_group():
    ...


@router.put("event-chains/{event-chain-id}")
async def update_event_chain():
    ...
