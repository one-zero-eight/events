from fastapi import FastAPI
from pydantic import BaseModel
from starlette.middleware.sessions import SessionMiddleware

from src.app.routers import routers
from src.config import settings

app = FastAPI(
    title=settings.APP_TITLE,
    description=settings.APP_DESCRIPTION,
    version=settings.APP_VERSION,
    servers=[
        {"url": "", "description": "Current"},
        {"url": "https://api.innohassle.ru", "description": "Production environment"},
    ],
    root_path_in_servers=False,
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


@app.get("/", tags=["Root"])
async def version() -> VersionInfo:
    return VersionInfo()
