__all__ = ["app"]

from fastapi import FastAPI, Request
from fastapi.openapi.docs import get_swagger_ui_html
from starlette.middleware.cors import CORSMiddleware

from src.api import docs
from src.api.lifespan import lifespan
from src.api.routers import routers
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
    ],
    root_path=settings.app_root_path,
    root_path_in_servers=False,
    swagger_ui_oauth2_redirect_url=None,
    swagger_ui_parameters={"tryItOutEnabled": True, "persistAuthorization": True, "filter": True},
    generate_unique_id_function=docs.generate_unique_operation_id,
    lifespan=lifespan,
    docs_url=None,
    redoc_url=None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

for router in routers:
    app.include_router(router)

if settings.environment == Environment.DEVELOPMENT:
    import logging
    import warnings

    warnings.warn("Enable sqlalchemy logging")
    logging.basicConfig()
    logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)


@app.get("/docs", tags=["System"], include_in_schema=False)
async def swagger_ui_html(request: Request):
    root_path = request.scope.get("root_path", "").rstrip("/")
    openapi_url = root_path + app.openapi_url

    return get_swagger_ui_html(
        openapi_url=openapi_url,
        title=app.title + " - Swagger UI",
        swagger_js_url="https://api.innohassle.ru/swagger/swagger-ui-bundle.js",
        swagger_css_url="https://api.innohassle.ru/swagger/swagger-ui.css",
        swagger_favicon_url="https://api.innohassle.ru/swagger/favicon.png",
    )
