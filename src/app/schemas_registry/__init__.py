__all__ = ["router"]

from fastapi import APIRouter

router = APIRouter(prefix="/schemas", tags=["Schemas Registry"])

# Register all schemas and routes
import src.app.schemas_registry.routes  # noqa: E402, F401
