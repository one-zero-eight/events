import re
from fastapi import FastAPI
from fastapi.routing import APIRoute
from pydantic import BaseModel
from starlette.middleware.sessions import SessionMiddleware

from src.app.routers import routers
from src.config import settings


def generate_unique_operation_id(route: APIRoute) -> str:
    # Better names for operationId in OpenAPI schema.
    # It is needed because clients generate code based on these names.
    # Requires pair (tag name + function name) to be unique.
    # See fastapi.utils:generate_unique_id (default implementation).
    operation_id = f"{route.tags[0]}_{route.name}".lower()
    operation_id = re.sub(r"\W+", "_", operation_id)
    return operation_id


app = FastAPI(
    title=settings.APP_TITLE,
    description=settings.APP_DESCRIPTION,
    version=settings.APP_VERSION,
    servers=[
        {"url": "", "description": "Current"},
        {"url": "https://api.innohassle.ru", "description": "Production environment"},
    ],
    root_path_in_servers=False,
    generate_unique_id_function=generate_unique_operation_id,
)

app.add_middleware(
    SessionMiddleware, secret_key=settings.SESSION_SECRET_KEY.get_secret_value()
)

for router in routers:
    app.include_router(router)


class VersionInfo(BaseModel):
    title = settings.APP_TITLE
    description = settings.APP_DESCRIPTION
    version = settings.APP_VERSION


@app.get("/", tags=["System"])
async def version() -> VersionInfo:
    return VersionInfo()
