import re

from fastapi.routing import APIRoute
from pydantic import BaseModel, Field

from src.config import settings
from src.schemas import UpdateEventGroup

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.repositories.event_groups import AbstractEventGroupRepository
    from src.repositories.users import AbstractUserRepository
    from src.repositories.tags import AbstractTagRepository


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


async def setup_predefined_data(
    event_group_repository: "AbstractEventGroupRepository",
    tag_repository: "AbstractTagRepository",
    user_repository: "AbstractUserRepository",
):
    import json
    from src.schemas import CreateEventGroup, CreateUser, CreateTag
    from src.repositories.predefined import PredefinedRepository
    from pydantic import parse_file_as

    class Categories(BaseModel):
        class Category(BaseModel):
            path: str

        categories: list[Category] = Field(default_factory=list)

    # ------------------- Predefined data -------------------

    with (settings.PREDEFINED_DIR / "innopolis_user_data.json").open(encoding="utf-8") as users_file:
        users_json = json.load(users_file)

    categories = parse_file_as(Categories, settings.PREDEFINED_DIR / "categories.json")
    categories_jsons = []

    for category in categories.categories:
        with (settings.PREDEFINED_DIR / category.path).open(encoding="utf-8") as category_file:
            category_json = json.load(category_file)
            categories_jsons.append(category_json)

    predefined_repository = PredefinedRepository.from_jsons(users_json, categories_jsons)
    predefined_tags = predefined_repository.get_tags()
    predefined_event_groups = predefined_repository.get_event_groups()
    predefined_users = predefined_repository.get_users()

    # create new groups and update existing groups
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
    created_groups = await event_group_repository.batch_create(_create_event_groups)
    # update existing groups
    await event_group_repository.batch_update(_update_event_groups)

    for group in created_groups + existing_groups:
        alias_x_group[group.alias] = group

    # create tags
    _create_tags = [CreateTag(**tag.dict()) for tag in predefined_tags]
    db_tags = await tag_repository.batch_create_or_read(_create_tags)
    alias_x_tag = {(tag.alias, tag.type): tag for tag in db_tags}

    # map tags to groups
    event_group_id_x_tags_ids = dict()
    for i, predefined_event_group in enumerate(predefined_event_groups):
        db_event_group_id = alias_x_group[predefined_event_group.alias].id
        tag_ids = [alias_x_tag[(tag.alias, tag.type)].id for tag in predefined_event_group.tags]
        event_group_id_x_tags_ids[db_event_group_id] = tag_ids

    # add tags to groups
    await tag_repository.batch_set_tags_to_event_group(event_group_id_x_tags_ids)

    # create users
    _create_users = [CreateUser(**user.dict()) for user in predefined_users]
    db_users = await user_repository.batch_create_or_read(_create_users)

    user_id_x_group_ids = dict()
    for i, user in enumerate(predefined_users):
        user_id = db_users[i].id
        user_id_x_group_ids[user_id] = [alias_x_group[group_alias].id for group_alias in user.groups]
    # map users to groups
    await event_group_repository.batch_setup_groups(user_id_x_group_ids)


def generate_unique_operation_id(route: APIRoute) -> str:
    # Better names for operationId in OpenAPI schema.
    # It is needed because clients generate code based on these names.
    # Requires pair (tag name + function name) to be unique.
    # See fastapi.utils:generate_unique_id (default implementation).
    operation_id = f"{route.tags[0]}_{route.name}".lower()
    operation_id = re.sub(r"\W+", "_", operation_id)
    return operation_id
