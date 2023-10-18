# fmt: off
__all__ = [
    "CreateEventGroup", "ViewEventGroup", "UpdateEventGroup",
    "UserXFavoriteGroupView", "ListEventGroupsResponse",

    "CreateEvent", "ViewEvent", "UpdateEvent",
    "AddEventPatch", "ViewEventPatch", "UpdateEventPatch",

    "CreateUser", "ViewUser", "UpdateUser",
    "CreateTag", "ViewTag", "UpdateTag",
    "Ownership", "OwnershipEnum",
    # TODO: Implement worshops
    # "CreateWorkshop", "ViewWorkshop", "CheckIn", "Timeslot", "CreateTimeslot",
    "LinkedCalendarCreate", "LinkedCalendarView", "LinkedCalendarUpdate"
]
# fmt: on


from src.schemas.event_groups import (
    CreateEventGroup,
    ViewEventGroup,
    UpdateEventGroup,
    UserXFavoriteGroupView,
    ListEventGroupsResponse,
)
from src.schemas.events import CreateEvent, ViewEvent, UpdateEvent, AddEventPatch, ViewEventPatch, UpdateEventPatch
from src.schemas.users import CreateUser, ViewUser, UpdateUser
from src.schemas.linked import LinkedCalendarCreate, LinkedCalendarView, LinkedCalendarUpdate
from src.schemas.tags import CreateTag, ViewTag, UpdateTag
from src.schemas.ownership import Ownership, OwnershipEnum

# TODO: Implement worshops
# from src.schemas.workshops import CreateWorkshop, ViewWorkshop, CheckIn, Timeslot, CreateTimeslot
