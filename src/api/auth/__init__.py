__all__ = ["oauth", "router"]

from authlib.integrations.starlette_client import OAuth
from fastapi import APIRouter

router = APIRouter(prefix="/auth", tags=["Auth"])
oauth = OAuth()

# Register all OAuth applications and routes
import src.api.auth.common  # noqa: E402, F401
import src.api.auth.innopolis  # noqa: E402, F401
import src.api.auth.dev  # noqa: E402, F401
