__all__ = ["app"]

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from src import constants
from src.api.routers import routers
from src.config import settings
from src.config_schema import Environment
from src.storages.sql import SQLAlchemyStorage
from src.utils import generate_unique_operation_id, setup_repositories

app = FastAPI(
    title=constants.TITLE,
    summary=constants.SUMMARY,
    description=constants.DESCRIPTION,
    version=constants.VERSION,
    contact=constants.CONTACT_INFO,
    license_info=constants.LICENSE_INFO,
    openapi_tags=constants.TAGS_INFO,
    servers=[
        {"url": settings.app_root_path, "description": "Current"},
        {
            "url": "https://api.innohassle.ru/events/v0",
            "description": "Production environment",
        },
    ],
    root_path=settings.app_root_path,
    root_path_in_servers=False,
    swagger_ui_oauth2_redirect_url=None,
    swagger_ui_parameters={"tryItOutEnabled": True, "persistAuthorization": True, "filter": True},
    generate_unique_id_function=generate_unique_operation_id,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(SessionMiddleware, secret_key=settings.auth.session_secret_key.get_secret_value())


@app.on_event("startup")
async def startup_event():
    await setup_repositories()
    # await setup_predefined_data() moved into endpoint /update-predefined-data


@app.on_event("shutdown")
async def close_connection():
    from src.api.dependencies import Shared

    storage = Shared.f(SQLAlchemyStorage)
    await storage.close_connection()


for router in routers:
    app.include_router(router)

if settings.environment == Environment.DEVELOPMENT:
    import logging
    import warnings

    warnings.warn("Enable sqlalchemy logging")
    logging.basicConfig()
    logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)
