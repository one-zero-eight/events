__all__ = ["app", "setup_repositories"]

import re

from fastapi import FastAPI
from fastapi.routing import APIRoute
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.requests import Request
from starlette.responses import RedirectResponse

from src import constants
from src.app.routers import routers
from src.config import settings
from src.schemas import UpdateEventGroup


def generate_unique_operation_id(route: APIRoute) -> str:
    # Better names for operationId in OpenAPI schema.
    # It is needed because clients generate code based on these names.
    # Requires pair (tag name + function name) to be unique.
    # See fastapi.utils:generate_unique_id (default implementation).
    operation_id = f"{route.tags[0]}_{route.name}".lower()
    operation_id = re.sub(r"\W+", "_", operation_id)
    return operation_id


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


async def setup_repositories():
    from src.repositories.event_groups import SqlEventGroupRepository
    from src.repositories.users import SqlUserRepository
    from src.repositories.tags import SqlTagRepository
    from src.storages.sql import SQLAlchemyStorage
    from src.app.dependencies import Dependencies

    # ------------------- Repositories Dependencies -------------------
    storage = SQLAlchemyStorage.from_url(settings.DB_URL.get_secret_value())
    user_repository = SqlUserRepository(storage)
    event_group_repository = SqlEventGroupRepository(storage)
    tag_repository = SqlTagRepository(storage)

    Dependencies.set_storage(storage)
    Dependencies.set_user_repository(user_repository)
    Dependencies.set_event_group_repository(event_group_repository)
    Dependencies.set_tag_repository(tag_repository)

    await storage.create_all()


async def setup_predefined_data():
    import json
    from src.schemas import CreateEventGroup, CreateUser, CreateTag
    from src.repositories.predefined import PredefinedRepository

    # get repositories
    from src.app.dependencies import Dependencies

    tag_repository = Dependencies.get_tag_repository()
    event_group_repository = Dependencies.get_event_group_repository()
    user_repository = Dependencies.get_user_repository()

    # ------------------- Predefined data -------------------
    with (
        (settings.PREDEFINED_DIR / "innopolis_user_data.json").open(encoding="utf-8") as users_file,
        (settings.PREDEFINED_DIR / "predefined_event_groups.json").open(encoding="utf-8") as groups_file,
        (settings.PREDEFINED_DIR / "predefined_tags.json").open(encoding="utf-8") as tags_file,
    ):
        users_json = json.load(users_file)
        groups_json = json.load(groups_file)
        tags_json = json.load(tags_file)

    predefined_repository = PredefinedRepository.from_jsons(users_json, groups_json, tags_json)
    predefined_tags = predefined_repository.get_tags()
    predefined_event_groups = predefined_repository.get_event_groups()
    predefined_users = predefined_repository.get_users()

    _create_tags = [CreateTag(**tag.dict()) for tag in predefined_tags]
    db_tags = await tag_repository.batch_create_or_read(_create_tags)
    alias_x_tag = {(tag.alias, tag.type): tag for tag in db_tags}

    existing_groups = await event_group_repository.read_all()
    alias_x_group = {group.alias: group for group in existing_groups}
    _create_event_groups = [
        CreateEventGroup(**group.dict()) for group in predefined_event_groups if group.alias not in alias_x_group
    ]
    _update_event_groups = {
        alias_x_group[group.alias].id: UpdateEventGroup(**group.dict(exclude_unset=True))
        for group in predefined_event_groups
        if group.alias in alias_x_group
    }
    # create new groups
    db_event_groups = await event_group_repository.batch_create(_create_event_groups)

    # check existance of ics files
    for group in db_event_groups + existing_groups:
        alias_x_group[group.alias] = group

    # update existing groups
    await event_group_repository.batch_update(_update_event_groups)

    _create_users = [CreateUser(**user.dict()) for user in predefined_users]
    db_users = await user_repository.batch_create_or_read(_create_users)

    event_group_id_x_tags_ids = dict()
    for i, predefined_event_group in enumerate(predefined_event_groups):
        db_event_group_id = alias_x_group[predefined_event_group.alias].id
        tag_ids = [alias_x_tag[(tag.alias, tag.type)].id for tag in predefined_event_group.tags]
        event_group_id_x_tags_ids[db_event_group_id] = tag_ids

    await tag_repository.batch_add_tags_to_event_group(event_group_id_x_tags_ids)

    user_id_x_group_ids = dict()
    for i, user in enumerate(predefined_users):
        user_id = db_users[i].id
        user_id_x_group_ids[user_id] = [alias_x_group[group_alias].id for group_alias in user.groups]

    await event_group_repository.batch_setup_groups(user_id_x_group_ids)


@app.on_event("startup")
async def startup_event():
    await setup_repositories()
    await setup_predefined_data()


@app.on_event("shutdown")
async def close_connection():
    from src.app.dependencies import Dependencies

    storage = Dependencies.get_storage()
    await storage.close_connection()


for router in routers:
    app.include_router(router)


@app.get("/", tags=["System"], include_in_schema=False)
async def root(request: Request):
    # Redirect to docs
    return RedirectResponse(request.url_for("swagger_ui_html"), status_code=302)
