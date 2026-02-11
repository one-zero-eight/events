__all__ = ["app"]

from fastapi import FastAPI
from fastapi_swagger import patch_fastapi
from starlette.middleware.cors import CORSMiddleware

import src.logging_  # noqa: F401
from src.api import docs
from src.api.lifespan import lifespan
from src.config import settings
from src.config_schema import Environment

app = FastAPI(
    title=docs.TITLE,
    summary=docs.SUMMARY,
    description=docs.DESCRIPTION,
    version=docs.VERSION,
    contact=docs.CONTACT_INFO,
    license_info=docs.LICENSE_INFO,
    openapi_tags=docs.TAGS_INFO,
    servers=[
        {"url": settings.app_root_path, "description": "Current"},
        {
            "url": "https://api.innohassle.ru/events/v0",
            "description": "Production environment",
        },
        {
            "url": "https://api.innohassle.ru/events/staging-v0",
            "description": "Staging environment",
        },
    ],
    root_path=settings.app_root_path,
    root_path_in_servers=False,
    generate_unique_id_function=docs.generate_unique_operation_id,
    lifespan=lifespan,
    docs_url=None,
    redoc_url=None,
    swagger_ui_oauth2_redirect_url=None,
)

patch_fastapi(app)

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=settings.cors_allow_origin_regex,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from src.modules.event_groups.routes import router as router_event_groups  # noqa: E402
from src.modules.ics.routes import router as router_ics  # noqa: E402
from src.modules.parse.routes import router as router_parse  # noqa: E402
from src.modules.predefined.routes import router as router_predefined  # noqa: E402
from src.modules.tags.routes import router as router_tags  # noqa: E402
from src.modules.users.routes import router as router_users  # noqa: E402

app.include_router(router_event_groups)
app.include_router(router_ics)
app.include_router(router_parse)
app.include_router(router_predefined)
app.include_router(router_tags)
app.include_router(router_users)

if settings.environment == Environment.DEVELOPMENT:
    import logging

    from src.logging_ import logger

    logger.warning("Enable sqlalchemy logging")
    logging.basicConfig()
    logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)

# Prometheus metrics
if True:
    from prometheus_fastapi_instrumentator import Instrumentator

    Instrumentator(excluded_handlers=["/metrics"]).instrument(app).expose(app)
