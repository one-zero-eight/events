from pydantic import BaseModel
from typing import List

from schemas.EventChain import EventChain
from schemas.Tag import HasOwnerMixin, HasModeratorsMixin, HasTagMixin


class EventGroup(BaseModel, HasOwnerMixin, HasModeratorsMixin, HasTagMixin):
    id: str
    """Unique identifier for the object."""
    title: str
    """Short name for display and indexing."""
    synonyms: List[str]
    """Set of additional names for indexing."""
    summary: str
    """Short description, contains plain text only."""
    description: str
    """Full description, can contain various formats (markdown, html)."""
    connected_event_chains: List[EventChain]
    """Set of event chains included in this group regardless of anything (has higher priority than ignoring parent group)"""
    ignored_event_chains: List[EventChain]
    """Set of event chains ignored in this group regardless of anything (has higher priority than including parent group)."""
    imported_event_groups: List[EventGroup]
    """Set of parent groups from which event chains (inclusions and ignorings) will be inherited"""
