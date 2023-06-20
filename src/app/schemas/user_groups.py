from ._base import BaseSchema
from ._mixins import ObjectReference, HasIdMixin, CollectConfigMeta, ORMMixin


class PermissionStruct(BaseSchema):
    """
    Represents a permission structure with role name and a list of commands applicable to a group of users and events.
    """

    role_name: str
    """The name of the role."""
    commands: list[str]
    """The list of commands applicable to the role."""


class BaseUserGroup(BaseSchema):
    """
    Represents a group of users
    """

    title: str
    """Title of the object."""
    permission_struct: list[PermissionStruct]
    """PermissionName/ID and list of commands applicable to group of users and events."""
    user_map: dict["ObjectReference", PermissionStruct]
    """Pair of user and it’s role/status in group."""
    users: list["ObjectReference"]


class CreateUserGroup(BaseUserGroup):
    ...


class ViewUserGroup(BaseUserGroup, HasIdMixin, ORMMixin, metaclass=CollectConfigMeta):
    user_map: dict["ObjectReference", PermissionStruct]
    """Pair of user and it’s role/status in group."""
    users: list["ViewUser"]


# fix circular imports
from src.app.schemas.users import ViewUser

ViewUserGroup.update_forward_refs()
