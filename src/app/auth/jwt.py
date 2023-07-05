__all__ = [
    "create_access_token",
    "create_parser_token",
    "verify_user_token",
    "verify_parser_token",
    "UserTokenData",
]

from datetime import timedelta, datetime
from typing import Optional

from jose import JWTError, jwt
from pydantic import BaseModel, validator

from src.config import settings

ALGORITHM = "HS256"


class UserTokenData(BaseModel):
    user_id: Optional[int] = None

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
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY.get_secret_value(), algorithm=ALGORITHM)
    return encoded_jwt


def verify_user_token(token: str, credentials_exception) -> UserTokenData:
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY.get_secret_value(), algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None or not user_id.isdigit():
            raise credentials_exception
        token_data = UserTokenData(user_id=int(user_id))
        return token_data
    except JWTError:
        raise credentials_exception


def verify_parser_token(token: str, credentials_exception) -> bool:
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY.get_secret_value(), algorithms=[ALGORITHM])
        parser_data = payload.get("sub")
        if parser_data == "parser":
            return True
        raise credentials_exception
    except JWTError:
        raise credentials_exception
