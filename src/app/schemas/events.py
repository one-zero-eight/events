from ._base import BaseSchema
from ._mixins import HasIdMixin, ObjectReference, ORMMixin, CollectConfigMeta


class BaseEvent(BaseSchema):
    """
    Represents an event.
    """

    title: str
    """Short name for display and indexing."""
    synonyms: list[str]
    """Set of additional names for indexing."""
    summary: str
    """Short description, contains plain text only."""
    description: str
    """Full description, can contain various formats (markdown, html)."""


class CreateEvent(BaseEvent):
    event_chain: "ObjectReference"
    """The chain of events to which this event belongs. Event object cannot exist without attaching to the EventChain"""


class ViewEvent(BaseEvent, HasIdMixin, ORMMixin, metaclass=CollectConfigMeta):
    """
    Represents an event.
    """

    event_chain: "ViewEventChain"
    """The chain of events to which this event belongs. Event object cannot exist without attaching to the EventChain"""


# fix circular imports
from .event_chains import ViewEventChain

ViewEvent.update_forward_refs()
