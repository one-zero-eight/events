from src.app.schemas import CreateEventChain, ViewEventChain
from fastapi import APIRouter
from ._types import ID

router = APIRouter(prefix="/event-chains", tags=["Event Chains"])


@router.post("/")
async def create_event_chain(event_chain: CreateEventChain) -> ViewEventChain:
    ...


@router.put("/{event-chain-id}")
async def update_event_chain(
    event_chain_id: ID, event_chain: CreateEventChain
) -> ViewEventChain:
    ...
