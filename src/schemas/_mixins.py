from typing import Union, List


class HasOwnerMixin:
    """
    Represents the mixin for objects with an owner.
    """
    owner: Union[List['User'], List['UserGroup']]


class HasModeratorsMixin:
    """
    Represents the mixin for objects with moderators.
    """
    moderators: Union[List['User'], List['UserGroup']]


class HasTagMixin:
    tags: List['Tag']


# fix circular imports
from schemas.users import User
from schemas.user_groups import UserGroup
from schemas.tags import Tag
