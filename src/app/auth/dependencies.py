from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from src.app.auth.jwt import verify_token
from src.exceptions import CredentialsException

bearer_scheme = HTTPBearer(
    scheme_name="Bearer",
    description="Your JSON Web Token (JWT)",
)


def get_current_user_email(
    auth: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> str:
    token_data = verify_token(auth.credentials, CredentialsException())
    return token_data.email
