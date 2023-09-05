__all__ = ["app"]

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from src import constants
from src.app.routers import routers
from src.config import settings, Environment
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
        {"url": settings.APP_ROOT_PATH, "description": "Current"},
        {
            "url": "https://api.innohassle.ru/events/v0",
            "description": "Production environment",
        },
    ],
    root_path=settings.APP_ROOT_PATH,
    root_path_in_servers=False,
    swagger_ui_oauth2_redirect_url=None,
    generate_unique_id_function=generate_unique_operation_id,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ALLOW_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(SessionMiddleware, secret_key=settings.SESSION_SECRET_KEY.get_secret_value())


@app.on_event("startup")
async def startup_event():
    await setup_repositories()
    # await setup_predefined_data() moved into endpoint /update-predefined-data


@app.on_event("shutdown")
async def close_connection():
    from src.app.dependencies import Dependencies

    storage = Dependencies.get_storage()
    await storage.close_connection()


for router in routers:
    app.include_router(router)

if settings.ENVIRONMENT == Environment.DEVELOPMENT:
    import logging
    import warnings

    warnings.warn("Enable sqlalchemy logging")
    logging.basicConfig()
    logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)
