__all__ = ["lifespan"]

from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.config import settings
from src.storages.sql import SQLAlchemyStorage


async def setup_repositories() -> SQLAlchemyStorage:
    from src.repositories.users.repository import user_repository
    from src.repositories.event_groups.repository import event_group_repository
    from src.repositories.tags.repository import tag_repository
    from src.repositories.innohassle_accounts import innohassle_accounts

    # ------------------- Repositories Dependencies -------------------

    storage = SQLAlchemyStorage.from_url(settings.db_url.get_secret_value())

    user_repository.update_storage(storage)
    event_group_repository.update_storage(storage)
    tag_repository.update_storage(storage)
    await innohassle_accounts.update_key_set()

    return storage


@asynccontextmanager
async def lifespan(_app: FastAPI):
    from src.repositories.predefined.utils import setup_predefined_data

    # Application startup
    storage = await setup_repositories()
    await setup_predefined_data()
    yield

    # Application shutdown
    await storage.close_connection()
