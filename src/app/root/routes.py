from starlette.requests import Request
from starlette.responses import RedirectResponse

from src.app.dependencies import (
    EVENT_GROUP_REPOSITORY_DEPENDENCY,
    USER_REPOSITORY_DEPENDENCY,
    TAG_REPOSITORY_DEPENDENCY,
    VERIFY_PARSER_DEPENDENCY,
)
from src.app.root import router
from src.config import settings, Environment
from src.exceptions import (
    IncorrectCredentialsException,
    NoCredentialsException,
)


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
async def update_predefined_data(
    _: VERIFY_PARSER_DEPENDENCY,
    event_group_repository: EVENT_GROUP_REPOSITORY_DEPENDENCY,
    tag_repository: TAG_REPOSITORY_DEPENDENCY,
    user_repository: USER_REPOSITORY_DEPENDENCY,
):
    from src.utils import setup_predefined_data

    await setup_predefined_data(
        event_group_repository=event_group_repository,
        tag_repository=tag_repository,
        user_repository=user_repository,
    )


@router.get("/", tags=["System"], include_in_schema=False)
async def redirect_from_root(request: Request):
    # Redirect to docs
    return RedirectResponse(request.url_for("swagger_ui_html"), status_code=302)
