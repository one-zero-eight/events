from fastapi import FastAPI
from pydantic import BaseModel
from starlette.middleware.sessions import SessionMiddleware

from src.app.routers import routers
from src.app.auth import router as auth_router
from src.app.schemas import schemas_router

from src.app.config import settings

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key=settings.SESSION_SECRET_KEY)

app.include_router(schemas_router)
app.include_router(auth_router)

for router in routers:
    app.include_router(router)


class VersionInfo(BaseModel):
    version = settings.APP_VERSION
    description = settings.APP_DESCRIPTION


@app.get("/", tags=["Root"])
async def version() -> VersionInfo:
    return VersionInfo()
