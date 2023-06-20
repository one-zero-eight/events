from fastapi import FastAPI
from pydantic import BaseModel

from app.routers import routers
from app.schemas import schemas_router

app = FastAPI()

app.include_router(schemas_router)

for router in routers:
    app.include_router(router)


class VersionInfo(BaseModel):
    version = "1.0.0"
    description = "InNoHassle-Events API"


@app.get("/", tags=["Root"])
async def version() -> VersionInfo:
    return VersionInfo()
