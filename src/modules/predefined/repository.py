from src.logging_ import logger
from src.modules.event_groups.repository import event_group_repository
from src.modules.predefined import PredefinedStorage
from src.modules.users.repository import user_repository


class PredefinedRepository:
    storage: PredefinedStorage

    def update_storage(self, storage: PredefinedStorage):
        self.storage = storage

    async def get_user_predefined(self, user_id: int) -> list[int]:
        user = await user_repository.read(user_id)
        assert user is not None
        predefind_user = self.storage.get_user(user.email)
        if predefind_user is None:
            return []
        event_group_mapping = await event_group_repository.batch_read_ids_by_aliases(predefind_user.groups)
        if None in event_group_mapping.values():
            logger.warning(f"User {user.email} has invalid predefined groups: {predefind_user.groups}")
        return list(filter(None, event_group_mapping.values()))


predefined_repository: PredefinedRepository = PredefinedRepository()
