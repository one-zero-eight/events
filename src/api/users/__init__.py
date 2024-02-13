__all__ = ["router"]

from fastapi import APIRouter

from src.exceptions import IncorrectCredentialsException, NoCredentialsException

router = APIRouter(
    prefix="/users",
    tags=["Users"],
    responses={
        **IncorrectCredentialsException.responses,
        **NoCredentialsException.responses,
    },
)

# Register all schemas and routes
import src.schemas.users  # noqa: E402, F401
import src.api.users.routes  # noqa: E402, F401
