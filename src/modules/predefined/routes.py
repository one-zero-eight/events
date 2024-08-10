from fastapi import APIRouter

from src.api.dependencies import VERIFY_PARSER_DEPENDENCY
from src.exceptions import IncorrectCredentialsException
from src.modules.predefined.repository import predefined_repository
from src.modules.predefined.storage import JsonPredefinedUsers

router = APIRouter(prefix="", tags=["Predefined"])


@router.get(
    "/get-predefined-data",
    responses={200: {"description": "Predefined data"}, **IncorrectCredentialsException.responses},
)
async def get_predefined_data(_: VERIFY_PARSER_DEPENDENCY) -> JsonPredefinedUsers:
    return predefined_repository.storage


@router.post(
    "/update-predefined-data",
    responses={
        200: {
            "description": "Predefined data updated successfully",
        },
        **IncorrectCredentialsException.responses,
    },
)
async def update_predefined_data(_: VERIFY_PARSER_DEPENDENCY, user_storage: JsonPredefinedUsers):
    from src.modules.predefined.utils import setup_predefined_data_from_object

    setup_predefined_data_from_object(user_storage)
