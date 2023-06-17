from typing import List, Union
from schemas._base import BaseSchema
from ._mixins import HasOwnerMixin, HasModeratorsMixin


class Tag(BaseSchema):
    """
    Represents a tag.
    """
    tag_name: str


class TagModel(BaseSchema, HasOwnerMixin, HasModeratorsMixin):
    """Pair of user, and it’s role/status in group."""

    id: str
    """The unique identifier for the object."""
    title: str
    """The short name for display and indexing."""
    synonyms: List[str]
    """The additional names for indexing."""
    summary: str
    """The short description that contains plain text."""
    description: str
    """The full description that can contain various formats (e.g., markdown, HTML)."""
    owner: Union[List['User'], List['UserGroup']]
    parent_tag: 'Tag'
    """The parent tag that includes this tag."""
    children_tags: List['Tag']
    """The set of tags included in this category."""


# fix circular imports
from .users import User
from .user_groups import UserGroup

TagModel.update_forward_refs()
