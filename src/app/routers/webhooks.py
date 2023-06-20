from fastapi import APIRouter
from ._types import ID

router = APIRouter(prefix="/webhooks", tags=["Webhooks"])


@router.put("/{webhook_id}")
async def configure_webhook(weebhook_id: ID):
    ...


@router.post("/")
async def create_webhook():
    ...
