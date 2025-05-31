from src.logging_ import logger
from src.modules.event_groups.repository import event_group_repository
from src.modules.innohassle_accounts import innohassle_accounts
from src.modules.predefined.storage import JsonPredefinedUsers
from src.modules.users.repository import user_repository


class PredefinedRepository:
    storage: JsonPredefinedUsers

    def update_storage(self, storage: JsonPredefinedUsers):
        self.storage = storage

    async def get_user_predefined(self, user_id: int) -> list[int]:
        user = await user_repository.read(user_id)
        assert user is not None
        predefind_user = self.storage.get_user(user.email)
        group_aliases = []

        if predefind_user:
            group_aliases.extend(predefind_user.groups)

        innohassle_accounts_user = await innohassle_accounts.get_user_by_id(user.innohassle_id)
        if (
            innohassle_accounts_user
            and innohassle_accounts_user.innopolis_sso
            and innohassle_accounts_user.innopolis_sso.group
        ):
            academic_group = innohassle_accounts_user.innopolis_sso.group
            _ = self.storage.get_academic_group(academic_group)
            if _:
                group_aliases.append(_)
            logger.info(
                f"User {user.email} has academic group {innohassle_accounts_user.innopolis_sso.group}, from predefined: '{_}'"
            )
        if not group_aliases:
            return []
        event_group_mapping = await event_group_repository.batch_read_ids_by_aliases(group_aliases)
        if None in event_group_mapping.values():
            logger.warning(f"User {user.email} has invalid predefined groups: {predefind_user.groups}")
        return list(filter(None, event_group_mapping.values()))


predefined_repository: PredefinedRepository = PredefinedRepository()
