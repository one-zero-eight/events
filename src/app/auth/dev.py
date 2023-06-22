__all__ = []

from typing import Optional
from starlette.responses import RedirectResponse

from src.app.auth import router
from src.app.auth.jwt import create_access_token, Token
from src.config import settings, Environment

enabled = (
    bool(settings.DEV_AUTH_EMAIL) and settings.ENVIRONMENT == Environment.DEVELOPMENT
)
redirect_uri = settings.AUTH_REDIRECT_URI_PREFIX + "/dev"

if enabled:
    print(
        "WARNING: Dev auth provider is enabled! "
        "Use this only for development environment "
        "(otherwise, set ENVIRONMENT=production)."
    )

    @router.get("/dev/login")
    async def login_via_dev(email: Optional[str] = None):
        url = redirect_uri
        if email:
            url += "?email=" + email
        return RedirectResponse(redirect_uri, status_code=302)

    @router.get("/dev/token")
    async def auth_via_dev(email: Optional[str] = None) -> Token:
        email = email or settings.DEV_AUTH_EMAIL
        return create_access_token(email)
