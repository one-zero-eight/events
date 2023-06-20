from ._base import BaseSchema
from ._mixins import (
    ObjectReference,
    HasOwnerMixin,
    HasModeratorsMixin,
    HasTagMixin,
    HasIdMixin,
    ORMMixin,
    CollectConfigMeta,
)


class BaseEventGroup(HasOwnerMixin, HasModeratorsMixin, HasTagMixin):
    """
    Represents an event group.
    """

    title: str
    """Short name for display and indexing."""
    synonyms: list[str]
    """Set of additional names for indexing."""
    summary: str
    """Short description, contains plain text only."""
    description: str
    """Full description, can contain various formats (markdown, html)."""


class CreateEventGroup(BaseEventGroup):
    connected_event_chains: list["ObjectReference"]
    """Set of event chains included in this group regardless of anything (has higher priority than ignoring parent 
    group)"""
    ignored_event_chains: list["ObjectReference"]
    """Set of event chains ignored in this group regardless of anything (has higher priority than including parent 
    group)."""
    imported_event_groups: list["ObjectReference"]
    """Set of parent groups from which event chains (inclusions and ignorings) will be inherited"""


class ViewEventGroup(BaseEventGroup, HasIdMixin, ORMMixin, metaclass=CollectConfigMeta):
    """
    Represents an event group.
    """

    connected_event_chains: list["ViewEventChain"]
    """Set of event chains included in this group regardless of anything (has higher priority than ignoring parent 
    group)"""
    ignored_event_chains: list["ViewEventChain"]
    """Set of event chains ignored in this group regardless of anything (has higher priority than including parent 
    group)."""
    imported_event_groups: list["ViewEventGroup"]
    """Set of parent groups from which event chains (inclusions and ignorings) will be inherited"""


# fix circular imports
from .event_chains import ViewEventChain

ViewEventGroup.update_forward_refs()
