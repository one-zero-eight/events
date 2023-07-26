__all__ = ["app", "setup_repositories"]

import re

from fastapi import FastAPI
from fastapi.routing import APIRoute
from pydantic import BaseModel
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from src.app.routers import routers
from src.config import settings


def generate_unique_operation_id(route: APIRoute) -> str:
    # Better names for operationId in OpenAPI schema.
    # It is needed because clients generate code based on these names.
    # Requires pair (tag name + function name) to be unique.
    # See fastapi.utils:generate_unique_id (default implementation).
    operation_id = f"{route.tags[0]}_{route.name}".lower()
    operation_id = re.sub(r"\W+", "_", operation_id)
    return operation_id


app = FastAPI(
    title=settings.APP_TITLE,
    description=settings.APP_DESCRIPTION,
    version=settings.APP_VERSION,
    servers=[
        {"url": settings.APP_ROOT_PATH, "description": "Current"},
        {
            "url": "https://api.innohassle.ru/events/v0",
            "description": "Production environment",
        },
    ],
    root_path=settings.APP_ROOT_PATH,
    root_path_in_servers=False,
    generate_unique_id_function=generate_unique_operation_id,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(SessionMiddleware, secret_key=settings.SESSION_SECRET_KEY.get_secret_value())


async def setup_repositories():
    import json
    from src.schemas import CreateEventGroup, CreateUser, CreateTag
    from src.repositories.event_groups import SqlEventGroupRepository
    from src.repositories.users import SqlUserRepository, PredefinedRepository
    from src.repositories.tags import SqlTagRepository
    from src.storages.sql import SQLAlchemyStorage
    from src.app.dependencies import Dependencies

    storage = SQLAlchemyStorage.from_url(settings.DB_URL.get_secret_value())
    user_repository = SqlUserRepository(storage)
    event_group_repository = SqlEventGroupRepository(storage)
    tag_repository = SqlTagRepository(storage)

    Dependencies.set_storage(storage)
    Dependencies.set_user_repository(user_repository)
    Dependencies.set_event_group_repository(event_group_repository)
    Dependencies.set_tag_repository(tag_repository)

    await storage.create_all()

    with (
        settings.PREDEFINED_TAGS_FILE.open(encoding="utf-8") as tags_file,
        settings.PREDEFINED_GROUPS_FILE.open(encoding="utf-8") as groups_file,
        settings.PREDEFINED_USERS_FILE.open(encoding="utf-8") as users_file,
    ):
        users_json = json.load(users_file)
        groups_json = json.load(groups_file)
        tags_json = json.load(tags_file)

    predefined_repositories = PredefinedRepository.from_jsons(users_json, groups_json, tags_json)
    unique_tags = predefined_repositories.get_tags()
    db_tags = await tag_repository.batch_create_tag_if_not_exists([CreateTag(**tag.dict()) for tag in unique_tags])
    tags_mappping = {tag.alias: tag for tag in db_tags}

    unique_groups = predefined_repositories.get_groups()
    groups_to_create = [CreateEventGroup(**group.dict()) for group in unique_groups]

    db_groups = await event_group_repository.batch_create_group_if_not_exists(groups_to_create)
    path_x_group = {group.path: group for group in db_groups}

    group_id_x_tag_ids = dict()
    for i, group in enumerate(unique_groups):
        group_id = db_groups[i].id
        group_id_x_tag_ids[group_id] = [tags_mappping[tag].id for tag in group.tags]

    await tag_repository.batch_add_tags_to_event_group(group_id_x_tag_ids)

    users = predefined_repositories.get_users()
    db_users = await user_repository.batch_create_user_if_not_exists([CreateUser(**user.dict()) for user in users])
    user_id_x_group_ids = dict()
    for i, user in enumerate(users):
        user_id = db_users[i].id
        user_id_x_group_ids[user_id] = [path_x_group[group.path].id for group in user.groups]
    await event_group_repository.batch_setup_groups(user_id_x_group_ids)


@app.on_event("startup")
async def startup_event():
    await setup_repositories()


@app.on_event("shutdown")
async def close_connection():
    from src.app.dependencies import Dependencies

    storage = Dependencies.get_storage()
    await storage.close_connection()


for router in routers:
    app.include_router(router)


class VersionInfo(BaseModel):
    title = settings.APP_TITLE
    description = settings.APP_DESCRIPTION
    version = settings.APP_VERSION


@app.get("/", tags=["System"])
async def version() -> VersionInfo:
    return VersionInfo()
