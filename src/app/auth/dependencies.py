from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from starlette import status

from src.app.auth.jwt import verify_token

bearer_scheme = HTTPBearer(
    scheme_name="Bearer",
    description="Your JSON Web Token (JWT)",
)

credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)


def get_current_user_email(
    auth: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> str:
    token_data = verify_token(auth.credentials, credentials_exception)
    return token_data.email
