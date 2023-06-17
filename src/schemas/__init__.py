from schemas._base import BaseSchema

from schemas.event_chains import EventChain
from schemas.event_groups import EventGroup
from schemas.events import Event
from schemas.tags import Tag
from schemas.user_groups import UserGroup
from schemas.users import User

all_schemas = [
    Event,
    User,
    UserGroup,
    EventChain,
    EventGroup,
    Tag
]

for schema in all_schemas:
    schema.update_forward_refs()

__all__ = [*all_schemas, 'all_schemas', 'BaseSchema']

if __name__ == '__main__':
    from pprint import pprint

    pprint(all_schemas)
