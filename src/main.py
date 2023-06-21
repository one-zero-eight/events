from fastapi import FastAPI
from pydantic import BaseModel
from starlette.middleware.sessions import SessionMiddleware

from src.app.routers import routers
from src.config import settings

app = FastAPI()
app.add_middleware(
    SessionMiddleware, secret_key=settings.SESSION_SECRET_KEY.get_secret_value()
)

for router in routers:
    app.include_router(router)


class VersionInfo(BaseModel):
    version = settings.APP_VERSION
    description = settings.APP_DESCRIPTION


@app.get("/", tags=["Root"])
async def version() -> VersionInfo:
    return VersionInfo()
