from fastapi import APIRouter

from src.api.dependencies import VERIFY_PARSER_DEPENDENCY
from src.exceptions import IncorrectCredentialsException, NoCredentialsException

router = APIRouter("", tags=["Predefined"])


@router.post(
    "/update-predefined-data",
    responses={
        200: {
            "description": "Predefined data updated successfully",
        },
        **IncorrectCredentialsException.responses,
        **NoCredentialsException.responses,
    },
)
async def update_predefined_data(_: VERIFY_PARSER_DEPENDENCY):
    # TODO: Replace with json body
    from src.modules.predefined.utils import setup_predefined_data

    await setup_predefined_data()
