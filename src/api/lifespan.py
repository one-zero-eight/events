__all__ = ["lifespan"]

from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.config import settings
from src.storages.sql import SQLAlchemyStorage


async def setup_repositories() -> SQLAlchemyStorage:
    from src.modules.users.repository import user_repository
    from src.modules.event_groups.repository import event_group_repository
    from src.modules.tags.repository import tag_repository
    from src.modules.innohassle_accounts import innohassle_accounts

    # ------------------- Repositories Dependencies -------------------

    storage = SQLAlchemyStorage.from_url(settings.db_url.get_secret_value())

    user_repository.update_storage(storage)
    event_group_repository.update_storage(storage)
    tag_repository.update_storage(storage)
    await innohassle_accounts.update_key_set()

    return storage


def setup_predefined_data_from_file():
    import json
    from src.modules.predefined.storage import JsonPredefinedUsers
    from src.modules.predefined.utils import setup_predefined_data_from_object

    # check for file existing
    users_path = settings.predefined_dir / "innopolis_user_data.json"
    if not users_path.exists():
        users_json = {"users": []}
    else:
        with users_path.open(encoding="utf-8") as users_file:
            users_json = json.load(users_file)

    user_storage = JsonPredefinedUsers.from_jsons(users_json)
    setup_predefined_data_from_object(user_storage)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    # Application startup
    storage = await setup_repositories()
    setup_predefined_data_from_file()
    yield

    # Application shutdown
    await storage.close_connection()
