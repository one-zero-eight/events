from pydantic import BaseModel
from EventChain import EventChain


class Event(BaseModel):
    id: str
    """The unique identifier for the object."""
    description: str
    """A comment that tells in general terms what happens inside the vevent field"""
    vevent: VEVENT
    """Main fields - description, uid, dtstamp, start and end time, repeatability rule, location. 
    Can be an update (transfer, cancellation, change of fields) of another event or one several copies of repeatability (RRULE instanse).
    For recurring events, you may need to use the RECURRENCE-ID"""
    event_chain: EventChain
    """The chain of events to which this event belongs. Event object cannot exist without attaching to the EventChain"""
    sequence: int
    """It is important to designate a sequential number in the chain of events (SEQUENCE)"""
