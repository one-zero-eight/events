__all__ = ["router"]

from fastapi import APIRouter

router = APIRouter(prefix="", tags=["Ics files"])

# Register all schemas and routes
import src.app.ics.routes  # noqa: E402, F401
