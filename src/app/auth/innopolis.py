__all__ = []

from typing import Annotated

from authlib.integrations.base_client import MismatchingStateError
from fastapi import Depends
from pydantic import BaseModel, Field
from starlette.requests import Request
from starlette.responses import RedirectResponse

from src.app.auth import router, oauth
from src.app.auth.common import redirect_with_token, ensure_allowed_return_to
from src.app.auth.dependencies import get_current_user_id
from src.app.dependencies import Dependencies
from src.app.auth.jwt import create_access_token
from src.exceptions import NoCredentialsException, IncorrectCredentialsException
from src.schemas.users import CreateUser
from src.config import settings
from src.repositories.users.abc import AbstractUserRepository


class UserInfoFromSSO(BaseModel):
    email: str
    name: str | None = Field(alias="commonname")


enabled = bool(settings.INNOPOLIS_SSO_CLIENT_ID.get_secret_value())
redirect_uri = settings.INNOPOLIS_SSO_REDIRECT_URI

if enabled:
    innopolis_sso = oauth.register(
        "innopolis",
        client_id=settings.INNOPOLIS_SSO_CLIENT_ID.get_secret_value(),
        client_secret=settings.INNOPOLIS_SSO_CLIENT_SECRET.get_secret_value(),
        # OAuth client will fetch configuration on first request
        server_metadata_url="https://sso.university.innopolis.ru/adfs/.well-known/openid-configuration",
        client_kwargs={"scope": "openid"},
    )

    # Add type hinting
    oauth.innopolis: oauth.oauth2_client_cls  # noqa

    @router.get("/innopolis/login", include_in_schema=False)
    async def innopolis_login(return_to: str, request: Request):
        ensure_allowed_return_to(return_to)
        request.session.clear()  # Clear session cookie as it is used only during auth
        request.session["return_to"] = return_to
        return await oauth.innopolis.authorize_redirect(request, redirect_uri)

    @router.get("/innopolis/callback", include_in_schema=False)
    async def innopolis_callback(
        request: Request,
        user_repository: Annotated[AbstractUserRepository, Depends(Dependencies.get_user_repository)],
    ):
        try:
            token = await oauth.innopolis.authorize_access_token(request)
        except MismatchingStateError:
            # Session is different on 'login' and 'callback'
            return await recover_mismatching_state(request)

        user_info_dict: dict = token["userinfo"]
        user_info = UserInfoFromSSO(**user_info_dict)
        user = await user_repository.create_or_update(CreateUser(**user_info.dict()))

        return_to = request.session.pop("return_to")
        ensure_allowed_return_to(return_to)
        request.session.clear()  # Clear session cookie as it is used only during auth
        token = create_access_token(user.id)
        return redirect_with_token(return_to, token)

    async def recover_mismatching_state(request: Request):
        return_to = request.session.get("return_to")

        try:
            # Check if a user has access token
            user_id = await get_current_user_id(None, request.cookies.get(settings.AUTH_COOKIE_NAME))
        except (NoCredentialsException, IncorrectCredentialsException):
            user_id = None

        if return_to and user_id:
            # User has already authenticated in another tab,
            # and we know where to return a user.
            # Let's get them where they want to be.
            ensure_allowed_return_to(return_to)
            return RedirectResponse(return_to, status_code=302)

        if user_id is not None:
            # User has already authenticated in another tab,
            # but we don't know where to return a user.
            # Let's just return user to main page.
            return RedirectResponse("https://innohassle.ru", status_code=302)

        if return_to:
            # User is not authenticated,
            # and we know where to return a user after authentication.
            # Let's ask them to authenticate again.
            ensure_allowed_return_to(return_to)
            url = (
                request.url_for("innopolis_login")
                .replace(scheme="https", hostname="api.innohassle.ru", port="")
                .include_query_params(return_to=return_to)
            )
            return RedirectResponse(url, status_code=302)

        # We don't know anything, so let's just return user to main page.
        return RedirectResponse("https://innohassle.ru", status_code=302)
