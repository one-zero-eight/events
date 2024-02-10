__all__ = []

import warnings
from typing import Optional


from src.app.auth import router
from src.app.auth.common import redirect_with_token, ensure_allowed_return_to
from src.app.auth.jwt import create_access_token, create_parser_token
from src.schemas import CreateUser
from src.config import settings, Environment
from src.app.dependencies import Shared
from src.repositories.users import SqlUserRepository

enabled = bool(settings.dev_auth_email) and settings.environment == Environment.DEVELOPMENT

if enabled:
    warnings.warn(
        "Dev auth provider is enabled! "
        "Use this only for development environment "
        "(otherwise, set ENVIRONMENT=production)."
    )

    @router.get("/dev/login", include_in_schema=False)
    async def dev_login(
        return_to: str = "/",
        email: Optional[str] = None,
    ):
        ensure_allowed_return_to(return_to)
        email = email or settings.dev_auth_email
        user_repository = Shared.f(SqlUserRepository)
        user = await user_repository.create_or_update(CreateUser(email=email, name="Ivan Petrov"))
        token = create_access_token(user.id)
        return redirect_with_token(return_to, token)

    @router.get("/dev/token")
    async def get_dev_token(
        email: Optional[str] = None,
    ) -> str:
        email = email or settings.dev_auth_email
        user_repository = Shared.f(SqlUserRepository)
        user = await user_repository.create_or_update(CreateUser(email=email, name="Ivan Petrov"))
        return create_access_token(user.id)

    @router.get("/dev/parser-token")
    async def get_dev_parser_token() -> str:
        return create_parser_token()
