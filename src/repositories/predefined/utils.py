import json

from pydantic import BaseModel, Field

from src.config import settings
from src.repositories.predefined import PredefinedStorage
from src.schemas import CreateEventGroup, CreateTag, UpdateEventGroup


async def setup_predefined_data():
    from src.repositories.event_groups.repository import event_group_repository
    from src.repositories.tags.repository import tag_repository
    from src.repositories.predefined.repository import predefined_repository

    class Categories(BaseModel):
        class Category(BaseModel):
            path: str

        categories: list[Category] = Field(default_factory=list)

    # ------------------- Predefined data -------------------

    # check for file existing
    users_path = settings.predefined_dir / "innopolis_user_data.json"
    categories_path = settings.predefined_dir / "categories.json"
    if not users_path.exists():
        users_json = {"users": []}
    else:
        with (settings.predefined_dir / "innopolis_user_data.json").open(encoding="utf-8") as users_file:
            users_json = json.load(users_file)
    if not categories_path.exists():
        categories = Categories()
    else:
        with (settings.predefined_dir / "categories.json").open(encoding="utf-8") as categories_file:
            categories = Categories.model_validate_json(categories_file.read())
    categories_jsons = []

    for category in categories.categories:
        category_path = settings.predefined_dir / category.path
        if not category_path.exists():
            continue
        with (settings.predefined_dir / category.path).open(encoding="utf-8") as category_file:
            category_json = json.load(category_file)
            categories_jsons.append(category_json)

    predefined_storage = PredefinedStorage.from_jsons(users_json, categories_jsons)
    predefined_repository.update_storage(predefined_storage)
    predefined_tags = predefined_storage.get_tags()
    predefined_event_groups = predefined_storage.get_event_groups()

    # create new groups and update existing groups
    existing_groups = await event_group_repository.read_all()
    alias_x_group = {group.alias: group for group in existing_groups}
    _create_event_groups = [
        CreateEventGroup(**group.model_dump()) for group in predefined_event_groups if group.alias not in alias_x_group
    ]
    _update_event_groups = {
        alias_x_group[group.alias].id: UpdateEventGroup(**group.model_dump(exclude_unset=True))
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
