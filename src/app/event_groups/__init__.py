__all__ = ["router"]

from fastapi import APIRouter

router = APIRouter(prefix="/event-groups", tags=["Event Groups"])

# Register all schemas and routes
import src.schemas.event_groups  # noqa: E402, F401
import src.app.event_groups.routes  # noqa: E402, F401
