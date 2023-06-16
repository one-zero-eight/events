from typing import List, Union
from pydantic import BaseModel

from User import User
from UserGroup import UserGroup


class HasOwnerMixin(BaseModel):
    """
    Represents the mixin for objects with an owner.
    """
    owner: Union[List[User], List[UserGroup]]


class HasModeratorsMixin(BaseModel):
    """
    Represents the mixin for objects with moderators.
    """
    moderators: Union[List[User], List[UserGroup]]


class HasTagMixin(BaseModel):
    tags: List[Tag]


class Tag(BaseModel):
    """
    Represents a tag.
    """
    tag_name: str


class TagModel(BaseModel, HasOwnerMixin, HasModeratorsMixin):
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
    owner: Union[List[User], List[UserGroup]]
    parent_tag: Tag
    """The parent tag that includes this tag."""
    children_tags: List[Tag]
    """The set of tags included in this category."""
