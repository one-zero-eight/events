__all__ = ["get_current_user_id", "verify_parser"]

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from src.exceptions import (
    NoCredentialsException,
    IncorrectCredentialsException,
)
from src.repositories.tokens.repository import TokenRepository

bearer_scheme = HTTPBearer(
    scheme_name="Bearer",
    description="Your JSON Web Token (JWT)",
    bearerFormat="JWT",
    auto_error=False,  # We'll handle error manually
)


async def get_current_user_id(
    bearer: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> int:
    # Prefer header to cookie
    token = bearer and bearer.credentials
    if not token:
        raise NoCredentialsException()
    token_data = await TokenRepository.verify_user_token(token, IncorrectCredentialsException())
    return token_data.user_id


def verify_parser(
    bearer: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> bool:
    token = (bearer and bearer.credentials) or None
    if not token:
        raise NoCredentialsException()
    return TokenRepository.verify_parser_token(token, IncorrectCredentialsException())
