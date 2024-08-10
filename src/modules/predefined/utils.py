import json


from src.config import settings
from src.modules.predefined import PredefinedStorage


async def setup_predefined_data():
    from src.modules.predefined.repository import predefined_repository
    # ------------------- Predefined data -------------------

    # check for file existing
    users_path = settings.predefined_dir / "innopolis_user_data.json"
    if not users_path.exists():
        users_json = {"users": []}
    else:
        with users_path.open(encoding="utf-8") as users_file:
            users_json = json.load(users_file)

    predefined_storage = PredefinedStorage.from_jsons(users_json)
    predefined_repository.update_storage(predefined_storage)
