__all__ = ["router"]

from fastapi import APIRouter

router = APIRouter(prefix="/tags", tags=["Tags"])

# Register all schemas and routes
import src.schemas.tags  # noqa: E402, F401
import src.api.tags.routes  # noqa: E402, F401
