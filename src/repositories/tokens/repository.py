__all__ = ["TokenRepository"]

import datetime
import time

from authlib.jose import JWTClaims
from authlib.jose import jwt, JoseError
from pydantic import BaseModel

from src.repositories.innohassle_accounts import innohassle_accounts
from src.repositories.users.repository import user_repository
from src.schemas import CreateUser


def aware_utcnow() -> datetime.datetime:
    return datetime.datetime.now(datetime.timezone.utc)


class UserTokenData(BaseModel):
    user_id: int
    innohassle_id: str


class TokenRepository:
    @classmethod
    def decode_token(cls, token: str) -> JWTClaims:
        now = time.time()
        pub_key = innohassle_accounts.get_public_key()
        payload = jwt.decode(token, pub_key)
        payload.validate_exp(now, leeway=0)
        payload.validate_iat(now, leeway=0)
        return payload

    @classmethod
    async def fetch_user_id_or_create(cls, innohassle_id: str) -> int | None:
        user_id = await user_repository.read_id_by_innohassle_id(innohassle_id)
        if user_id is not None:
            return user_id

        innohassle_user = await innohassle_accounts.get_user_by_id(innohassle_id)
        if innohassle_user is None:
            return None
        user_id = await user_repository.read_id_by_email(innohassle_user.innopolis_sso.email)
        if user_id is not None:
            await user_repository.update_innohassle_id(user_id, innohassle_id)
            return user_id

        user = CreateUser(
            email=innohassle_user.innopolis_sso.email,
            name=innohassle_user.innopolis_sso.name,
            innohassle_id=innohassle_id,
        )
        user_id = (await user_repository.create(user)).id
        return user_id

    @classmethod
    async def verify_user_token(cls, token: str, credentials_exception) -> UserTokenData:
        try:
            payload = cls.decode_token(token)
            innohassle_id: str = payload.get("uid")
            if innohassle_id is None:
                raise credentials_exception
            user_id = await cls.fetch_user_id_or_create(innohassle_id)
            if user_id is None:
                raise credentials_exception
            return UserTokenData(user_id=user_id, innohassle_id=innohassle_id)
        except JoseError:
            raise credentials_exception

    @classmethod
    def verify_parser_token(cls, token: str, credentials_exception) -> bool:
        try:
            payload = cls.decode_token(token)
            parser_data = payload.get("sub")
            if parser_data == "parser":
                return True
            raise credentials_exception
        except JoseError:
            raise credentials_exception
