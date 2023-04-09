from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from starlette.middleware.cors import CORSMiddleware

from src.auth.routes import router as auth_router
from src.config import app_configs, settings
from src.database import database

app = FastAPI(**app_configs)

app.add_middleware(
    CORSMiddleware,
    # allow_origins=settings.CORS_ORIGINS,
    # allow_origin_regex=settings.CORS_ORIGINS_REGEX,
    allow_credentials=True,
    allow_methods=("GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"),
    # allow_headers=settings.CORS_HEADERS,
)


# @app.on_event("startup")
# async def startup() -> None:
#     await database.connect()
#
#
# @app.on_event("shutdown")
# async def shutdown() -> None:
#     await database.disconnect()


# redirect to docs
@app.get("/", include_in_schema=False, status_code=302)
async def redirect_to_docs() -> RedirectResponse:
    return RedirectResponse(url="/docs")


@app.get(
    "/healthcheck",
    responses={
        200: {
            "description": "OK",
            "content"    : {"application/json": {"example": {"status": "ok"}}}
        }
    },
    tags=["Healthcheck"]
)
async def healthcheck() -> dict[str, str]:
    """Healthcheck endpoint"""
    return {"status": "ok"}


app.include_router(auth_router, prefix="/auth", tags=["Auth"])
