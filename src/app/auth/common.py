from datetime import datetime, timedelta, timezone

from starlette.datastructures import URL
from starlette.responses import RedirectResponse

from src.app.auth import router
from src.config import settings
from src.exceptions import InvalidReturnToURL


def redirect_with_token(return_to: str, token: str):
    response = RedirectResponse(return_to, status_code=302)
    response.set_cookie(
        key=settings.AUTH_COOKIE_NAME,
        value=token,
        httponly=True,
        secure=True,
        domain=settings.AUTH_COOKIE_DOMAIN,
        expires=datetime.now().astimezone(tz=timezone.utc) + timedelta(days=90),
    )
    return response


def redirect_deleting_token(return_to: str):
    response = RedirectResponse(return_to, status_code=302)
    response.delete_cookie(
        key=settings.AUTH_COOKIE_NAME,
        httponly=True,
        secure=True,
        domain=settings.AUTH_COOKIE_DOMAIN,
    )
    return response


def ensure_allowed_return_to(return_to: str):
    try:
        url = URL(return_to)
        if url.hostname is None:
            return  # Ok. Allow returning to current domain
        if url.hostname in settings.AUTH_ALLOWED_DOMAINS:
            return  # Ok. Hostname is allowed (does not check port)
    except (AssertionError, ValueError):
        pass  # Bad. URL is malformed
    raise InvalidReturnToURL()


@router.get("/logout", include_in_schema=False)
async def logout(return_to: str):
    ensure_allowed_return_to(return_to)
    return redirect_deleting_token(return_to)
