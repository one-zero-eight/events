__all__ = []

import warnings

from src.api.auth import router
from src.api.auth.common import redirect_with_token, ensure_allowed_return_to
from src.api.auth.jwt import create_access_token, create_parser_token
from src.schemas import CreateUser
from src.config import settings, Environment
from src.api.dependencies import Shared
from src.repositories.users import SqlUserRepository

if settings.environment == Environment.DEVELOPMENT:
    warnings.warn(
        "Dev auth provider is enabled! "
        "Use this only for development environment "
        "(otherwise, set ENVIRONMENT=production)."
    )

    @router.get("/dev/login")
    async def dev_login(email: str = settings.test_user_email, return_to: str = "/"):
        ensure_allowed_return_to(return_to)
        user_repository = Shared.f(SqlUserRepository)
        user = await user_repository.create_or_update(CreateUser(email=email, name="Unnamed"))
        token = create_access_token(user.id)
        return redirect_with_token(return_to, token)

    @router.get("/dev/token")
    async def get_dev_token(email: str = settings.test_user_email) -> str:
        user_repository = Shared.f(SqlUserRepository)
        user = await user_repository.create_or_update(CreateUser(email=email, name="Unnamed"))
        return create_access_token(user.id)

    @router.get("/dev/parser-token")
    async def get_dev_parser_token() -> str:
        return create_parser_token()
