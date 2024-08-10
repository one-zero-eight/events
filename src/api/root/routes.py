from fastapi import APIRouter
from starlette.requests import Request
from starlette.responses import RedirectResponse

from src.api.dependencies import VERIFY_PARSER_DEPENDENCY
from src.config import settings, Environment
from src.exceptions import IncorrectCredentialsException, NoCredentialsException

router = APIRouter(prefix="")


@router.get(
    "/update-predefined-data",
    responses={
        200: {
            "description": "Predefined data updated successfully",
        },
        **IncorrectCredentialsException.responses,
        **NoCredentialsException.responses,
    },
    tags=["System"],
    include_in_schema=settings.environment == Environment.DEVELOPMENT,
)
async def update_predefined_data(_: VERIFY_PARSER_DEPENDENCY):
    from src.repositories.predefined.utils import setup_predefined_data

    await setup_predefined_data()


@router.get("/", tags=["System"], include_in_schema=False)
async def redirect_from_root(request: Request):
    # Redirect to docs
    return RedirectResponse(request.url_for("swagger_ui_html"), status_code=302)
