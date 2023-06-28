__all__ = []

from typing import Optional

from src.app.auth import router
from src.app.auth.common import redirect_with_token
from src.app.auth.jwt import create_access_token
from src.config import settings, Environment

enabled = (
    bool(settings.DEV_AUTH_EMAIL) and settings.ENVIRONMENT == Environment.DEVELOPMENT
)

if enabled:
    print(
        "WARNING: Dev auth provider is enabled! "
        "Use this only for development environment "
        "(otherwise, set ENVIRONMENT=production)."
    )

    @router.get("/dev/login", include_in_schema=False)
    async def dev_login(return_to: str, email: Optional[str] = None):
        email = email or settings.DEV_AUTH_EMAIL
        token = create_access_token(email)
        return redirect_with_token(return_to, token)

    @router.get("/dev/token")
    async def get_dev_token(email: Optional[str] = None) -> str:
        email = email or settings.DEV_AUTH_EMAIL
        return create_access_token(email)
