__all__ = ["router"]

from fastapi import APIRouter

router = APIRouter(prefix="/users", tags=["Users"])

# Register all schemas and routes
import src.schemas.users  # noqa: E402, F401
import src.api.users.routes  # noqa: E402, F401
