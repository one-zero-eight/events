from enum import Enum

from pydantic import BaseModel


class UserPermissionEnum(Enum):
    GUEST = 'guest',
    USER = 'user',
    ADMIN = 'admin'


class User(BaseModel):
    """
    Pydantic model that represents a user instance
    """

    id: str
    """
    Unique identifier for the object.
    """
    permission: UserPermissionEnum
    """
    User’s general permission level to api (might be derived from general api).
    """
