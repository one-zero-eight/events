__all__ = [
    "create_access_token",
    "create_parser_token",
    "verify_user_token",
    "verify_parser_token",
    "UserTokenData",
]

from datetime import timedelta, datetime
from typing import Optional

from authlib.jose import jwt, JoseError
from pydantic import BaseModel, validator

from src.api.dependencies import Shared
from src.config import settings
from src.repositories.users import SqlUserRepository

ALGORITHM = "RS256"


class UserTokenData(BaseModel):
    user_id: Optional[int] = None

    # TODO[pydantic]: We couldn't refactor the `validator`, please replace it by `field_validator` manually.
    # Check https://docs.pydantic.dev/dev-v2/migration/#changes-to-validators for more information.
    @validator("user_id", pre=True, always=True)
    def cast_to_int(cls, v):
        if isinstance(v, str):
            return int(v)
        return v


def create_access_token(user_id: int) -> str:
    access_token = _create_access_token(
        data={"sub": str(user_id)},
        expires_delta=timedelta(days=90),
    )
    return access_token


def create_parser_token() -> str:
    access_token = _create_access_token(
        data={"sub": "parser"},
        expires_delta=timedelta(days=365),
    )
    return access_token


def _create_access_token(data: dict, expires_delta: timedelta) -> str:
    payload = data.copy()
    issued_at = datetime.utcnow()
    expire = issued_at + expires_delta
    payload.update({"exp": expire, "iat": issued_at})
    encoded_jwt = jwt.encode({"alg": ALGORITHM}, payload, settings.auth.jwt_private_key.get_secret_value())
    return str(encoded_jwt, "utf-8")


async def verify_user_token(token: str, credentials_exception) -> UserTokenData:
    try:
        user_repository = Shared.f(SqlUserRepository)
        payload = jwt.decode(token, settings.auth.jwt_public_key)
        user_id: str = payload.get("sub")
        if user_id is None or not user_id.isdigit():
            raise credentials_exception
        converted_user_id = int(user_id)
        if await user_repository.read(converted_user_id) is None:
            raise credentials_exception

        token_data = UserTokenData(user_id=converted_user_id)
        return token_data
    except JoseError:
        raise credentials_exception


def verify_parser_token(token: str, credentials_exception) -> bool:
    try:
        payload = jwt.decode(token, settings.auth.jwt_public_key)
        parser_data = payload.get("sub")
        if parser_data == "parser":
            return True
        raise credentials_exception
    except JoseError:
        raise credentials_exception
