from ._mixins import (
    ObjectReference,
    HasOwnerMixin,
    HasModeratorsMixin,
    HasTagMixin,
    HasIdMixin,
    CollectConfigMeta,
    ORMMixin,
)


class BaseEventChain(HasOwnerMixin, HasModeratorsMixin, HasTagMixin):
    """
    Represents an event chain.
    """

    title: str
    """The short name for display and indexing."""
    synonyms: list[str]
    """The additional names for indexing."""
    summary: str
    """The short description that contains plain text."""
    description: str
    """The full description that can contain various formats (e.g., markdown, HTML)."""


class CreateEventChain(BaseEventChain):
    """
    Represents an event chain.
    """

    events: list["ObjectReference"]
    """The events included in this chain."""
    connected_event_groups: list["ObjectReference"]
    """The event groups to which this chain has been added."""
    ignored_event_groups: list["ObjectReference"]
    """The event groups in which this chain should be ignored."""


class ViewEventChain(BaseEventChain, HasIdMixin, ORMMixin, metaclass=CollectConfigMeta):
    """
    Represents an event chain.
    """

    events: list["ViewEvent"]
    """The events included in this chain."""
    connected_event_groups: list["ViewEventGroup"]
    """The event groups to which this chain has been added."""
    ignored_event_groups: list["ViewEventGroup"]
    """The event groups in which this chain should be ignored."""


# fix circular imports
from src.app.schemas.events import ViewEvent
from src.app.schemas.event_groups import ViewEventGroup

ViewEventChain.update_forward_refs()
