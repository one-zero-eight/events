__all__ = []

from authlib.integrations.base_client import MismatchingStateError
from pydantic import BaseModel, Field
from starlette.requests import Request
from starlette.responses import RedirectResponse, JSONResponse

from src.api.auth import router, oauth
from src.api.auth.common import redirect_with_token, ensure_allowed_return_to
from src.api.auth.dependencies import get_current_user_id
from src.api.dependencies import Shared
from src.api.auth.jwt import create_access_token
from src import constants
from src.exceptions import NoCredentialsException, IncorrectCredentialsException
from src.repositories.users import SqlUserRepository
from src.schemas.users import CreateUser
from src.config import settings


class UserInfoFromSSO(BaseModel):
    email: str
    name: str | None = Field(None, alias="commonname")


if settings.innopolis_sso is not None:
    innopolis_sso = oauth.register(
        "innopolis",
        client_id=settings.innopolis_sso.client_id,
        client_secret=settings.innopolis_sso.client_secret.get_secret_value(),
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
        return await oauth.innopolis.authorize_redirect(
            request, settings.innopolis_sso.redirect_uri, resource=settings.innopolis_sso.resource_id
        )

    @router.get("/innopolis/callback", include_in_schema=False)
    async def innopolis_callback(request: Request):
        # Check if there are any error from SSO
        error = request.query_params.get("error")
        if error:
            description = request.query_params.get("error_description")
            print("SSO Error:", error, description)
            return JSONResponse(status_code=403, content={"error": error, "description": description})

        try:
            token = await oauth.innopolis.authorize_access_token(request)
            print("SSO Token received:", token)
        except MismatchingStateError:
            # Session is different on 'login' and 'callback'
            print("MismatchingStateError")
            return await recover_mismatching_state(request)

        user_info_dict: dict = token["userinfo"]
        user_info = UserInfoFromSSO(**user_info_dict)
        user_repository = Shared.f(SqlUserRepository)
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
            user_id = await get_current_user_id(None, request.cookies.get(settings.auth.cookie_name))
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
            return RedirectResponse(constants.WEBSITE_URL, status_code=302)

        if return_to:
            # User is not authenticated,
            # and we know where to return a user after authentication.
            # Let's ask them to authenticate again.
            ensure_allowed_return_to(return_to)
            url = request.url_for("innopolis_login").include_query_params(return_to=return_to)
            return RedirectResponse(url, status_code=302)

        # We don't know anything, so let's just return user to main page.
        return RedirectResponse(constants.WEBSITE_URL, status_code=302)
