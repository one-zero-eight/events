from enum import Enum

from schemas._base import BaseSchema


class UserPermissionEnum(Enum):
    GUEST = 'guest',
    USER = 'user',
    ADMIN = 'admin'


class User(BaseSchema):
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
