from typing import List

from pydantic import BaseModel

from schemas.EventGroup import EventGroup
from schemas.Event import Event
from schemas.Tag import HasOwnerMixin, HasModeratorsMixin, HasTagMixin


class EventChain(BaseModel, HasOwnerMixin, HasModeratorsMixin, HasTagMixin):
    """
    Represents the main Pydantic model.
    """
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
    events: List[Event]
    """The events included in this chain."""
    connected_event_groups: List[EventGroup]
    """The event groups to which this chain has been added."""
    ignored_event_groups: List[EventGroup]
    """The event groups in which this chain should be ignored."""
