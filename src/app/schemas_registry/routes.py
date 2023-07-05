from typing import Any

from pydantic import BaseModel

from src.app.schemas_registry import router
from src.schemas import CreateEventGroup, ViewEventGroup, UserXGroupView, ListEventGroupsResponse, CreateUser, ViewUser

# fmt: off
all_schemas = [
    CreateUser, ViewUser,
    CreateEventGroup, ViewEventGroup, UserXGroupView, ListEventGroupsResponse
]
# fmt: on

schema_dict = {schema.__name__: schema.schema(ref_template="#/components/schemas/{model}") for schema in all_schemas}


class Schemas(BaseModel):
    """
    Represents a dictionary of all schemas.
    """

    schemas: dict[str, Any]


@router.get(
    "/",
    response_model=Schemas,
    responses={
        200: {
            "description": "Returns a dictionary of all schemas.",
            "content": {"application/json": {"example": {"schemas": schema_dict}}},
        }
    },
)
async def schemas():
    """
    Get a list of all schemas
    """
    return {"schemas": schema_dict}


__all__ = ["all_schemas", "router"]
