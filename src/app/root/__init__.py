__all__ = ["router"]

from fastapi import APIRouter

router = APIRouter(prefix="")

# Register all schemas and routes
import src.app.root.routes  # noqa: E402, F401
