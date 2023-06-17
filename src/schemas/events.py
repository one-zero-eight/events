from schemas._base import BaseSchema


class VEVENT(BaseSchema):
    summary: str | None
    """The short name for display and indexing."""
    description: str | None
    """The full description that can contain various formats (e.g., markdown, HTML)."""
    dtstamp: str | None
    """The date and time when the object was created."""
    dtstart: str | None
    """The date and time when the object was created."""


class Event(BaseSchema):
    id: str
    """The unique identifier for the object."""
    description: str
    """A comment that tells in general terms what happens inside the vevent field"""
    vevent: VEVENT
    """Main fields - description, uid, dtstamp, start and end time, repeatability rule, location. 
    Can be an update (transfer, cancellation, change of fields) of another event or one several copies of repeatability (RRULE instanse).
    For recurring events, you may need to use the RECURRENCE-ID"""
    event_chain: 'EventChain'
    """The chain of events to which this event belongs. Event object cannot exist without attaching to the EventChain"""
    sequence: int
    """It is important to designate a sequential number in the chain of events (SEQUENCE)"""


# fix circular imports
from schemas.event_chains import EventChain

Event.update_forward_refs()
