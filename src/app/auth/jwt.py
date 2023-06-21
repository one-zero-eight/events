__all__ = ("create_access_token", "verify_token", "Token", "TokenData")

from datetime import timedelta, datetime
from typing import Optional

from jose import JWTError, jwt
from pydantic import BaseModel

from src.config import settings

ALGORITHM = "HS256"


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: Optional[str] = None


def create_access_token(user_id: str):
    access_token = _create_access_token(
        data={"sub": user_id},
        expires_delta=timedelta(days=90),
    )
    return Token(access_token=access_token, token_type="bearer")


def _create_access_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str, credentials_exception):
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
        return token_data
    except JWTError:
        raise credentials_exception
