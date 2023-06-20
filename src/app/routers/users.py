from fastapi import APIRouter
from ._types import ID

router = APIRouter(prefix="/users", tags=["Users"])
