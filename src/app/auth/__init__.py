__all__ = ("oauth", "router", "get_current_user_email")

from authlib.integrations.starlette_client import OAuth
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from starlette import status

from src.app.auth.jwt import verify_token

router = APIRouter(prefix="/auth", tags=["Auth"])
oauth = OAuth()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def get_current_user_email(data: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    return verify_token(data, credentials_exception)


# Register all OAuth applications and routes
import src.app.auth.innopolis  # noqa
