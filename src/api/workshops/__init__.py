__all__ = ["router"]

from fastapi import APIRouter

router = APIRouter(prefix="/workshops", tags=["Workshops"])

# Register all schemas and routes
import src.schemas.workshops  # noqa: E402, F401
import src.api.workshops.routes  # noqa: E402, F401
