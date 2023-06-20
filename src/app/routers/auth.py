from fastapi import APIRouter
from ._types import ID

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/login")
async def auth_user(email: str, password: str) -> str:
    ...


@router.post("/registration")
async def register_user(email: str, password: str) -> str:
    ...
