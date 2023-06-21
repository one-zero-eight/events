from typing import Union, Any

from fastapi import APIRouter
from pydantic import BaseModel

from ._base import BaseSchema
from .event_chains import ViewEventChain, CreateEventChain
from .event_groups import ViewEventGroup, CreateEventGroup
from .events import ViewEvent, CreateEvent
from .tags import ViewTag, CreateTag
from .user_groups import ViewUserGroup, CreateUserGroup
from .users import ViewUser, CreateUser

# fmt: off
all_schemas = [
    ViewEvent, CreateEvent,
    ViewUser, CreateUser,
    ViewUserGroup, CreateUserGroup,
    ViewEventChain, CreateEventChain,
    ViewEventGroup, CreateEventGroup,
    ViewTag, CreateTag,
]
# fmt: on

schemas_router = APIRouter(tags=["Schemas"])
schema_dict = {
    schema.__name__: schema.schema(ref_template="#/components/schemas/{model}")
    for schema in all_schemas
}


class Schemas(BaseModel):
    """
    Represents a dictionary of all schemas.
    """

    schemas: dict[str, Any]


@schemas_router.get(
    "/schemas",
    response_model=Schemas,
    responses={
        200: {
            "description": "Returns a dictionary of all schemas.",
            "content": {"application/json": {"example": {"schemas": schema_dict}}},
        }
    },
)
async def schemas():
    return {"schemas": schema_dict}


__all__ = [*all_schemas, "BaseSchema", "schemas_router"]
