__all__ = []

from typing import Annotated

from fastapi import Depends
from pydantic import BaseModel, Field
from starlette.requests import Request

from src.app.auth import router, oauth
from src.app.dependencies import get_user_repository
from src.repositories import UserRepository
from src.app.auth.jwt import create_access_token, Token
from src.config import settings


class UserInfoFromSSO(BaseModel):
    email: str
    name: str | None = Field(alias="commonname")
    status: str | None = Field(alias="Status")


enabled = bool(settings.INNOPOLIS_SSO_CLIENT_ID.get_secret_value())
redirect_uri = settings.AUTH_REDIRECT_URI_PREFIX + "/innopolis"

if enabled:
    innopolis_sso = oauth.register(
        "innopolis",
        client_id=settings.INNOPOLIS_SSO_CLIENT_ID.get_secret_value(),
        client_secret=settings.INNOPOLIS_SSO_CLIENT_SECRET.get_secret_value(),
        # OAuth client will fetch configuration on first request
        server_metadata_url="https://sso.university.innopolis.ru/adfs/.well-known/openid-configuration",
        client_kwargs={"scope": "openid"},
    )

    @router.get("/innopolis/login")
    async def login_via_innopolis(request: Request):
        return await oauth.innopolis.authorize_redirect(request, redirect_uri)

    @router.get("/innopolis/token")
    async def get_token_via_innopolis(
        request: Request,
        user_repository: Annotated[UserRepository, Depends(get_user_repository)],
    ) -> Token:
        token = await oauth.innopolis.authorize_access_token(request)
        user_info_dict: dict = token["userinfo"]
        user_info = UserInfoFromSSO(**user_info_dict)
        email = user_info.email
        user_repository.update_or_create_user(
            email, **user_info.dict(exclude={"email"})
        )
        return create_access_token(email)
