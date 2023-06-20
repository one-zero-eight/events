from ._base import BaseSchema
from ._mixins import (
    ObjectReference,
    HasOwnerMixin,
    HasModeratorsMixin,
    HasIdMixin,
    CollectConfigMeta,
    ORMMixin,
)


class BaseTag(HasOwnerMixin, HasModeratorsMixin):
    """
    Represents a tag.
    """

    title: str
    """The short name for display and indexing."""
    synonyms: list[str]
    """The additional names for indexing."""
    summary: str
    """The short description that contains plain text."""
    description: str
    """The full description that can contain various formats (e.g., markdown, HTML)."""


class CreateTag(BaseTag):
    """
    Represents a tag.
    """

    parent_tag: "ObjectReference"
    """The parent tag that includes this tag."""
    children_tags: list["ObjectReference"]
    """The set of tags included in this category."""


class ViewTag(BaseTag, HasIdMixin, ORMMixin, metaclass=CollectConfigMeta):
    """
    Represents a tag.
    """

    parent_tag: "ViewTag"
    """The parent tag that includes this tag."""
    children_tags: list["ViewTag"]
    """The set of tags included in this category."""


# fix circular imports

ViewTag.update_forward_refs()
