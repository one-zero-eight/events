from typing import Dict, List

from schemas._base import BaseSchema


class PermissionStruct(BaseSchema):
    """
    Represents a permission structure with role name and a list of commands applicable to a group of users and events.
    """
    role_name: str
    """The name of the role."""
    commands: List[str]
    """The list of commands applicable to the role."""


class UserGroup(BaseSchema):
    """Represents a group of users"""

    id: str
    """Unique identifier for the object."""

    title: str
    """Title of the object."""

    permission_struct: PermissionStruct
    """PermissionName/ID and list of commands applicable to group of users and events."""
    user_map: Dict['User', PermissionStruct]
    """Pair of user and it’s role/status in group."""


# fix circular imports
from schemas.users import User

UserGroup.update_forward_refs()
