__all__ = ["router"]

from fastapi import APIRouter

router = APIRouter(prefix="", tags=["ICS"])

# Register all schemas and routes
import src.app.ics.routes  # noqa: E402, F401
