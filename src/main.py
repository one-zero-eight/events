from fastapi import FastAPI
from pydantic import BaseModel

from src.app.routers import routers
from src.app.schemas import schemas_router

from src.app.config import settings

app = FastAPI()

app.include_router(schemas_router)

for router in routers:
    app.include_router(router)


class VersionInfo(BaseModel):
    version = settings.APP_VERSION
    description = settings.APP_DESCRIPTION


@app.get("/", tags=["Root"])
async def version() -> VersionInfo:
    return VersionInfo()
